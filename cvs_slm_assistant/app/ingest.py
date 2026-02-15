import json
import re
from pathlib import Path
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import docx2txt

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "kb"
DOCS_DIR = KB_DIR / "docs"
INDEX_PATH = KB_DIR / "faiss.index"
CHUNKS_PATH = KB_DIR / "chunks.jsonl"

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# -------------------------------
# File Readers
# -------------------------------
def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)

def read_docx(path: Path) -> str:
    return docx2txt.process(str(path)) or ""

def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

# -------------------------------
# Cleaning + Chunking
# -------------------------------
def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += max(1, chunk_size - overlap)
    return chunks

# -------------------------------
# Ingestion Main
# -------------------------------
def ingest_documents():
    KB_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Looking for documents in: {DOCS_DIR}")

    embedder = SentenceTransformer(EMBED_MODEL_NAME)

    all_chunks: List[Dict] = []

    files = list(DOCS_DIR.glob("*"))
    if not files:
        raise RuntimeError("No documents found in kb/docs/. Please add PDFs/DOCX/TXT files.")

    for file in files:
        print(f"Processing: {file.name}")

        if file.suffix.lower() == ".pdf":
            raw_text = read_pdf(file)
        elif file.suffix.lower() == ".docx":
            raw_text = read_docx(file)
        elif file.suffix.lower() == ".txt":
            raw_text = read_txt(file)
        else:
            print(f"Skipping unsupported file: {file.name}")
            continue

        raw_text = clean_text(raw_text)

        if not raw_text.strip():
            print(f"Warning: Empty text in {file.name}")
            continue

        chunks = chunk_text(raw_text)

        for chunk in chunks:
            all_chunks.append({
                "chunk_id": len(all_chunks),
                "source": file.name,
                "text": chunk
            })

    if not all_chunks:
        raise RuntimeError("No valid chunks generated. Check document content.")

    print(f"Total chunks created: {len(all_chunks)}")

    texts = [c["text"] for c in all_chunks]

    print("Generating embeddings...")
    embeddings = embedder.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    dim = embeddings.shape[1]

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("✅ Ingestion complete")
    print(f"Saved index to: {INDEX_PATH}")
    print(f"Saved chunks to: {CHUNKS_PATH}")

if __name__ == "__main__":
    ingest_documents()
