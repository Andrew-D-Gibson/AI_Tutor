import argparse
import hashlib
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).resolve().parent
RAG_DIR = BASE_DIR / "RAG_Files"
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "rag_files"
EMBED_MODEL = "all-MiniLM-L6-v2"


def chunk_text(text, max_chars=1000, overlap=200):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for p in paragraphs:
        if not current:
            current = p
            continue
        if len(current) + 2 + len(p) <= max_chars:
            current = current + "\n\n" + p
        else:
            chunks.append(current)
            current = p

    if current:
        chunks.append(current)

    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            final_chunks.append(chunk)
            continue
        start = 0
        while start < len(chunk):
            end = min(len(chunk), start + max_chars)
            final_chunks.append(chunk[start:end])
            if end == len(chunk):
                break
            start = max(0, end - overlap)

    return final_chunks


def read_text_file(path):
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def build_collection(reset=False):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    if reset:
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )


def ingest(reset=False):
    if not RAG_DIR.exists():
        raise FileNotFoundError(f"RAG directory not found: {RAG_DIR}")

    collection = build_collection(reset=reset)

    documents = []
    metadatas = []
    ids = []

    for path in sorted(RAG_DIR.glob("*")):
        if path.is_dir():
            continue
        text = read_text_file(path)
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            digest = hashlib.sha1(chunk.encode("utf-8")).hexdigest()[:12]
            doc_id = f"{path.name}-{i}-{digest}"
            documents.append(chunk)
            metadatas.append({"source": path.name, "chunk": i})
            ids.append(doc_id)

    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Ingested {len(documents)} chunks from {RAG_DIR}")
    print(f"Database saved to {DB_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Ingest RAG files into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Reset the collection")
    args = parser.parse_args()

    ingest(reset=args.reset)


if __name__ == "__main__":
    main()