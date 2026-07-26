import os
import math
import time
import uuid
import requests
from pathlib import Path

# Config from environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
MEILI_URL = os.getenv("MEILI_URL", "http://meilisearch:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "your_master_key_here")

INDEX_NAME = "rag_docs"
EMBED_MODEL = "llama3.2"  # or another embedding-capable model
DOCS_PATH = Path("/docs")
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128


def log(msg):
    print(f"[INGEST] {msg}", flush=True)


def ensure_meili_index():
    headers = {
        "X-Meili-API-Key": MEILI_MASTER_KEY,
        "Content-Type": "application/json",
    }
    r = requests.get(f"{MEILI_URL}/indexes/{INDEX_NAME}", headers=headers)
    if r.status_code == 200:
        log(f"Index '{INDEX_NAME}' already exists.")
        return

    log(f"Creating index '{INDEX_NAME}'...")
    r = requests.post(
        f"{MEILI_URL}/indexes",
        headers=headers,
        json={"uid": INDEX_NAME, "primaryKey": "id"},
    )
    r.raise_for_status()
    log("Index created.")


def list_files():
    exts = {".pdf", ".txt", ".md"}
    files = []
    for root, _, filenames in os.walk(DOCS_PATH):
        for name in filenames:
            p = Path(root) / name
            if p.suffix.lower() in exts:
                files.append(p)
    log(f"Found {len(files)} files.")
    return files


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".txt" or path.suffix.lower() == ".md":
        return path.read_text(encoding="utf-8", errors="ignore")

    if path.suffix.lower() == ".pdf":
        try:
            import fitz  # PyMuPDF
        except ImportError:
            log("PyMuPDF not installed. Run: pip install pymupdf")
            return ""

        text = []
        with fitz.open(path) as doc:
            for page in doc:
                text.append(page.get_text())
        return "\n".join(text)

    return ""


def chunk_text(text: str):
    tokens = text.split()
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        if not chunk_tokens:
            break
        chunks.append(" ".join(chunk_tokens))
        start = end - CHUNK_OVERLAP
        if start < 0:
            start = 0
    return chunks


def embed_text(chunk: str):
    # Ollama /api/embeddings
    url = f"{OLLAMA_URL}/api/embeddings"
    r = requests.post(url, json={"model": EMBED_MODEL, "prompt": chunk})
    r.raise_for_status()
    data = r.json()
    return data.get("embedding")


def index_chunks(docs):
    headers = {
        "X-Meili-API-Key": MEILI_MASTER_KEY,
        "Content-Type": "application/json",
    }
    r = requests.post(
        f"{MEILI_URL}/indexes/{INDEX_NAME}/documents",
        headers=headers,
        json=docs,
    )
    r.raise_for_status()
    log(f"Indexed {len(docs)} chunks.")


def process_file(path: Path):
    log(f"Processing: {path}")
    text = read_text(path)
    if not text.strip():
        log(f"Empty or unreadable: {path}")
        return []

    chunks = chunk_text(text)
    docs = []
    for i, chunk in enumerate(chunks):
        emb = embed_text(chunk)
        if emb is None:
            log(f"Failed embedding for chunk {i} in {path}")
            continue

        doc_id = str(uuid.uuid4())
        docs.append(
            {
                "id": doc_id,
                "source_path": str(path),
                "chunk_index": i,
                "chunk_count": len(chunks),
                "text": chunk,
                "embedding": emb,
            }
        )

        if (i + 1) % 10 == 0:
            log(f"Embedded {i + 1}/{len(chunks)} chunks for {path}")

    return docs


def main():
    log("Starting RAG ingestion...")
    ensure_meili_index()
    files = list_files()

    total_docs = 0
    batch = []

    for f in files:
        docs = process_file(f)
        batch.extend(docs)

        # index in batches of 50
        if len(batch) >= 50:
            index_chunks(batch)
            total_docs += len(batch)
            batch = []

    if batch:
        index_chunks(batch)
        total_docs += len(batch)

    log(f"Finished ingestion. Total chunks indexed: {total_docs}")


if __name__ == "__main__":
    main()
