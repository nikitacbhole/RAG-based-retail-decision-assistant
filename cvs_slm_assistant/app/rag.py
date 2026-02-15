import json
from pathlib import Path
from typing import List, Dict, Tuple
import faiss
from sentence_transformers import SentenceTransformer

KB_DIR = Path("kb")
INDEX_PATH = KB_DIR / "faiss.index"
CHUNKS_PATH = KB_DIR / "chunks.jsonl"

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder

def load_index() -> faiss.Index:
    if not INDEX_PATH.exists():
        raise FileNotFoundError("FAISS index not found. Run: python app/ingest.py")
    return faiss.read_index(str(INDEX_PATH))

def load_chunks() -> List[Dict]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError("chunks.jsonl not found. Run: python app/ingest.py")
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def retrieve(query: str, top_k: int = 3) -> List[Dict]:
    index = load_index()
    chunks = load_chunks()
    embedder = get_embedder()

    q_vec = embedder.encode([query], normalize_embeddings=True).astype("float32")
    _, I = index.search(q_vec, top_k)

    results = []
    for idx in I[0]:
        if idx == -1:
            continue
        results.append(chunks[int(idx)])
    return results

def build_context(retrieved: List[Dict], max_chars: int = 4000) -> Tuple[str, List[Dict]]:
    parts, kept, total = [], [], 0
    for c in retrieved:
        block = f"[SOURCE: {c['source']} | chunk_id={c['chunk_id']}]\n{c['text'].strip()}\n"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        kept.append(c)
        total += len(block)
    return "\n".join(parts), kept
