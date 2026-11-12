# Fieldnotes RAG

A local PDF question-answering app. It extracts selectable PDF text, splits it into overlapping chunks, and uses BM25 to find relevant passages. Answers quote up to three matching source sentences with document and page citations; retrieval and answer selection run locally without an API key.

## Run

```powershell
python -m pip install -r requirements.txt
streamlit run streamlit_ui.py
```

The app automatically indexes `.pdf` and `.PDF` files beside `app.py`. You can also upload PDFs for the current session. Search results show the strongest matching source excerpts and citations; the app does not call an external AI service.

## Chunk size

The default is approximately 700 tokens with 100 tokens of overlap. That is a good starting point for report-style documents: chunks usually retain enough context to explain a point while remaining focused for retrieval. Chunk size should be based on the length of meaningful passages, not the total size of a PDF. Use 400-600 tokens for short, narrowly structured sections; try 800-1,000 when explanations span multiple paragraphs. Keep overlap around 10-20% so ideas near boundaries are not lost.

Token counts use a four-characters-per-token estimate. Compare a few representative questions and the retrieved passages before locking in settings. Scanned/image-only PDFs need OCR before indexing.

## Tests

```powershell
python -m pytest -q
```