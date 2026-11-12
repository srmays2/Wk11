from __future__ import annotations

import streamlit as st

from app import ROOT
from rag_engine import BM25Index, extract_chunks, extractive_answer


st.set_page_config(page_title="Fieldnotes | Document Q&A", page_icon="F", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');
    :root { --ink:#18231d; --muted:#66736b; --paper:#f7f7f1; --line:#dce2d9; --green:#315f45; --lime:#c4dd71; --rust:#c45b3c; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:var(--paper); background-image:radial-gradient(#d8ded4 0.65px, transparent 0.65px); background-size:18px 18px; }
    .block-container { max-width:1320px; padding-top:2.2rem; padding-bottom:4rem; }
    h1, h2, h3 { font-family:'Newsreader',Georgia,serif !important; letter-spacing:0 !important; color:var(--ink); }
    h1 { font-size:3rem !important; line-height:1.02 !important; }
    [data-testid="stSidebar"] { background:#e9eee6; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] h2 { font-size:1.25rem; }
    .eyebrow { font:500 0.72rem 'DM Mono',monospace; letter-spacing:0.08em; text-transform:uppercase; color:var(--green); }
    .lede { color:var(--muted); max-width:650px; font-size:1rem; }
    .rule { border-top:1px solid var(--line); margin:1.5rem 0; }
    .source-row { padding:0.65rem 0; border-bottom:1px solid var(--line); font-size:0.88rem; }
    .source-meta { color:var(--muted); font:0.7rem 'DM Mono',monospace; }
    .answer { background:#fff; border-left:4px solid var(--green); padding:1.15rem 1.35rem; border-radius:2px; }
    .answer p { line-height:1.65; }
    .stButton > button[kind="primary"] { background:var(--green); border:0; color:white; border-radius:3px; font-weight:600; }
    .stButton > button[kind="primary"]:hover { background:#244b35; border:0; }
    input, textarea { border-radius:3px !important; }
    code, .mono { font-family:'DM Mono',monospace; }
    </style>
    """,
    unsafe_allow_html=True,
)


def local_documents() -> list[tuple[str, bytes]]:
    files = sorted(
        (path for path in ROOT.iterdir() if path.suffix.casefold() == ".pdf"),
        key=lambda path: path.name.casefold(),
    )
    return [(path.name, path.read_bytes()) for path in files]


@st.cache_data(show_spinner=False)
def cached_chunks(
    documents: tuple[tuple[str, bytes], ...], chunk_tokens: int, overlap_tokens: int
):
    return extract_chunks(documents, chunk_tokens, overlap_tokens)


st.markdown('<div class="eyebrow">FIELDNOTES / DOCUMENT INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("Ask the source material.")
st.markdown(
    '<p class="lede">Search across your reports and inspect matching passages with page-level citations.</p>',
    unsafe_allow_html=True,
)

documents = local_documents()
uploaded = st.file_uploader("Add PDFs to this session", type=["pdf"], accept_multiple_files=True)
if uploaded:
    documents.extend((file.name, file.getvalue()) for file in uploaded)

with st.sidebar:
    st.markdown('<div class="eyebrow">INDEX SETTINGS</div>', unsafe_allow_html=True)
    chunk_tokens = st.slider("Chunk size (approx. tokens)", min_value=300, max_value=1200, value=700, step=100)
    overlap_tokens = st.slider("Overlap (approx. tokens)", min_value=0, max_value=300, value=100, step=20)
    top_k = st.slider("Passages to retrieve", min_value=1, max_value=10, value=5)
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown("**Chunking note**")
    st.caption("700 tokens with 100 tokens of overlap is a starting point for report-style PDFs. Tune it if answers need more surrounding context or retrieval is too broad.")

if overlap_tokens >= chunk_tokens:
    st.error("Overlap must be smaller than chunk size.")
    st.stop()

document_payload = tuple(documents)
if not document_payload:
    st.warning("No PDFs found. Add PDF files beside app.py or upload them above.")
    st.stop()

try:
    with st.spinner("Reading PDFs and building the search index..."):
        chunks = cached_chunks(document_payload, chunk_tokens, overlap_tokens)
except Exception as error:
    st.error(f"Could not read a PDF: {error}")
    st.stop()

if not chunks:
    st.error("No selectable text was found in these PDFs. Scanned documents need OCR before they can be indexed.")
    st.stop()

indexed_sources = {chunk.source for chunk in chunks}
unindexed_sources = sorted(
    {name for name, _ in document_payload} - indexed_sources,
    key=str.casefold,
)
if unindexed_sources:
    st.warning(
        "No selectable text was found in: "
        + ", ".join(unindexed_sources)
        + ". These documents need OCR before they can be searched."
    )

index = BM25Index(chunks)
doc_count = len({chunk.source for chunk in chunks})
left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown('<div class="eyebrow">QUERY</div>', unsafe_allow_html=True)
    with st.form("query_form"):
        question = st.text_area(
            "Your question",
            placeholder="What do these reports say about how AI changes software engineering work?",
            label_visibility="collapsed",
            height=100,
        )
        submitted = st.form_submit_button("Find an answer", type="primary", use_container_width=True)
    st.caption(f"{doc_count} documents · {len(chunks)} chunks · roughly {chunk_tokens} tokens per chunk")

with right:
    st.markdown('<div class="eyebrow">IN THIS INDEX</div>', unsafe_allow_html=True)
    for source in sorted({chunk.source for chunk in chunks}, key=str.casefold):
        source_chunks = [chunk for chunk in chunks if chunk.source == source]
        pages = max(chunk.page_end for chunk in source_chunks)
        st.markdown(
            f'<div class="source-row">{source}<br><span class="source-meta">{pages} pages · {len(source_chunks)} chunks</span></div>',
            unsafe_allow_html=True,
        )

if submitted:
    if not question.strip():
        st.warning("Enter a question to search the indexed documents.")
        st.stop()

    results = index.search(question, limit=top_k)
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">RETRIEVED EVIDENCE</div>', unsafe_allow_html=True)
    if not results:
        st.info("No matching passages were found. Try using terms that appear in the documents.")
        st.stop()

    with st.expander(f"Inspect {len(results)} retrieved passages", expanded=False):
        for result in results:
            st.markdown(f"**[{result.chunk.citation}]** · relevance {result.score:.2f}")
            st.write(result.chunk.text)

    st.markdown('<div class="eyebrow">CITED ANSWER</div>', unsafe_allow_html=True)
    st.caption("Closest matching source sentences; they may be related evidence rather than an exact answer.")
    answer = extractive_answer(question.strip(), results)
    if answer:
        st.write(answer)
    else:
        st.info("The retrieved passages do not contain a clear answer sentence. Inspect the passages above.")