"""
RAG Pipeline for the Digital Junior Analyst.
Handles document ingestion, chunking, embedding, and FAISS-based retrieval.
Uses google-genai SDK with the v1 API endpoint to bypass v1beta limitations.
"""
from __future__ import annotations

import os
import hashlib
from typing import List, Tuple

from dotenv import load_dotenv

try:
    from langchain_core.embeddings import Embeddings as LCEmbeddings
except ImportError:
    LCEmbeddings = object  # fallback if not available

load_dotenv()


# ---------------------------------------------------------------------------
# Custom Embedder — google-genai SDK with v1 API (avoids v1beta 404 errors)
# ---------------------------------------------------------------------------

class GeminiEmbedder(LCEmbeddings):
    """
    Custom embeddings class using google-genai SDK with http_options api_version=v1.
    Confirmed working models: gemini-embedding-001, gemini-embedding-2
    """

    def __init__(self, api_key: str, model: str = "models/gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        from google import genai
        self._client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1"},
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts in batches of 20."""
        all_embeddings = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            result = self._client.models.embed_content(
                model=self.model,
                contents=batch,
            )
            for emb in result.embeddings:
                all_embeddings.append(list(emb.values))
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        result = self._client.models.embed_content(
            model=self.model,
            contents=[text],
        )
        return list(result.embeddings[0].values)


# ---------------------------------------------------------------------------
# Document Schema
# ---------------------------------------------------------------------------
class Document:
    """Simple document container."""
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(source={self.metadata.get('source', '?')}, len={len(self.page_content)})"


# ---------------------------------------------------------------------------
# Text Chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str, source: str, title: str,
                chunk_size: int = 1200, chunk_overlap: int = 200) -> List[Document]:
    """Split a long string into overlapping chunks."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    pieces = splitter.split_text(text)
    return [
        Document(
            page_content=piece,
            metadata={"source": source, "title": title, "chunk_index": i}
        )
        for i, piece in enumerate(pieces)
    ]


# ---------------------------------------------------------------------------
# Ingestion Functions
# ---------------------------------------------------------------------------

def ingest_text(text: str, source: str = "Uploaded Document",
                title: str = "Uploaded Document") -> List[Document]:
    """Ingest a raw text string."""
    return _chunk_text(text, source=source, title=title)


def ingest_pdf(file_bytes: bytes, filename: str) -> List[Document]:
    """Ingest a PDF from bytes."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        full_text = "\n\n".join(
            page.extract_text() or "" for page in reader.pages
        )
        return _chunk_text(full_text, source=filename, title=filename)
    except ImportError:
        raise ImportError("pypdf not installed. Run: pip install pypdf")


def ingest_csv(file_bytes: bytes, filename: str) -> List[Document]:
    """Ingest a CSV — convert rows to natural language sentences."""
    import io
    import pandas as pd
    df = pd.read_csv(io.BytesIO(file_bytes))
    rows_text = []
    for _, row in df.iterrows():
        row_str = " | ".join(f"{col}: {val}" for col, val in row.items())
        rows_text.append(row_str)
    full_text = f"CSV File: {filename}\n\n" + "\n".join(rows_text)
    return _chunk_text(full_text, source=filename, title=filename)


# ---------------------------------------------------------------------------
# Vector Store Manager
# ---------------------------------------------------------------------------

def _doc_list_fingerprint(docs: List[Document]) -> str:
    combined = "".join(d.page_content[:100] for d in docs)
    return hashlib.md5(combined.encode()).hexdigest()


class VectorStoreManager:
    """
    Manages a FAISS vector store using custom GeminiEmbedder (v1 API).
    """

    def __init__(self):
        self._store = None
        self._fingerprint: str | None = None

    @property
    def is_ready(self) -> bool:
        return self._store is not None

    def build(self, docs: List[Document], api_key: str) -> None:
        """Build the FAISS index from Document objects."""
        from langchain_community.vectorstores import FAISS

        fingerprint = _doc_list_fingerprint(docs)
        if fingerprint == self._fingerprint and self._store is not None:
            return

        embedder = GeminiEmbedder(api_key=api_key)
        texts = [d.page_content for d in docs]
        metadatas = [d.metadata for d in docs]

        self._store = FAISS.from_texts(texts, embedder, metadatas=metadatas)
        self._fingerprint = fingerprint

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve top-k chunks. Returns list of (Document, score)."""
        if not self.is_ready:
            raise RuntimeError("Vector store not built yet. Call build() first.")

        results = self._store.similarity_search_with_score(query, k=k)
        out = []
        for lc_doc, score in results:
            doc = Document(
                page_content=lc_doc.page_content,
                metadata=lc_doc.metadata,
            )
            out.append((doc, float(score)))
        return out

    def retrieve_text(self, query: str, k: int = 5) -> str:
        """Return retrieved chunks as a formatted context string."""
        results = self.retrieve(query, k=k)
        parts = []
        for i, (doc, score) in enumerate(results, 1):
            title = doc.metadata.get("title", doc.metadata.get("source", "Unknown"))
            parts.append(f"--- Source {i}: {title} ---\n{doc.page_content}")
        return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Demo Data Loader
# ---------------------------------------------------------------------------

def load_demo_documents() -> List[Document]:
    """Load and chunk the built-in synthetic demo financial documents."""
    from demo_data import DEMO_DOCUMENTS
    all_docs: List[Document] = []
    for entry in DEMO_DOCUMENTS:
        chunks = _chunk_text(
            text=entry["content"].strip(),
            source=entry["source"],
            title=entry["title"],
        )
        all_docs.extend(chunks)
    return all_docs


# ---------------------------------------------------------------------------
# Global singleton store
# ---------------------------------------------------------------------------
_global_store = VectorStoreManager()


def get_store() -> VectorStoreManager:
    """Return the global VectorStoreManager singleton."""
    return _global_store
