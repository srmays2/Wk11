from __future__ import annotations

import os
from pathlib import Path

from openai import OpenAI

from rag_engine import (
    BM25Index,
    SYSTEM_PROMPT,
    SearchResult,
    build_user_prompt,
    extract_chunks,
    extractive_answer,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "gpt-4o-mini"


class LocalRAG:
    def __init__(
        self,
        chunk_size: int = 700,
        overlap: int = 100,
        documents_dir: Path = ROOT,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.documents_dir = Path(documents_dir)
        self.index: BM25Index | None = None

    def build(self) -> LocalRAG:
        pdf_paths = sorted(
            (path for path in self.documents_dir.iterdir() if path.suffix.casefold() == ".pdf"),
            key=lambda path: path.name.casefold(),
        )
        documents = [(path.name, path.read_bytes()) for path in pdf_paths]
        chunks = extract_chunks(documents, self.chunk_size, self.overlap)
        self.index = BM25Index(chunks)
        return self

    def search(self, question: str, top_k: int = 5) -> list[SearchResult]:
        if self.index is None:
            raise RuntimeError("Build the LocalRAG index before searching.")
        return self.index.search(question, limit=top_k)


def generate_answer(
    question: str,
    results: list[SearchResult],
    model: str | None = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        response = OpenAI(api_key=api_key).chat.completions.create(
            model=model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, results)},
            ],
        )
        return response.choices[0].message.content or "The model returned an empty answer."

    answer = extractive_answer(question, results)
    if answer:
        return answer
    return "I could not find enough supporting evidence in the retrieved passages to answer this question."


if __name__ == "__main__":
    import streamlit_ui
