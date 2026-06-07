"""
Módulo RAG para TorresMack Chatbot.
Indexa documentos .txt y .pdf de la carpeta data/ y recupera
fragmentos relevantes para enriquecer las respuestas de DeepSeek.
"""

import os
import glob
import chromadb
import fitz  # pymupdf
from chromadb.utils import embedding_functions

# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────

DATA_DIR      = os.path.join(os.path.dirname(__file__), "..", "data")
CHROMA_DIR    = os.path.join(os.path.dirname(__file__), ".chroma")
COLLECTION    = "torresmack_docs"
EMBED_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K         = 3
CHUNK_SIZE    = 400
CHUNK_OVERLAP = 80

# ──────────────────────────────────────────────
# Embedding + ChromaDB
# ──────────────────────────────────────────────

_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)

_client = chromadb.PersistentClient(path=CHROMA_DIR)


def _get_collection():
    return _client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=_embed_fn,
        metadata={"hnsw:space": "cosine"},
    )


# ──────────────────────────────────────────────
# Lectura de PDF
# ──────────────────────────────────────────────

def _read_pdf(filepath: str) -> str:
    """Extrae todo el texto de un PDF con PyMuPDF."""
    doc = fitz.open(filepath)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


# ──────────────────────────────────────────────
# Chunking por párrafos
# ──────────────────────────────────────────────

def _chunk_text(text: str) -> list:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < CHUNK_SIZE:
            current = current + "\n\n" + para if current else para
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


# ──────────────────────────────────────────────
# Indexación
# ──────────────────────────────────────────────

def build_index(force: bool = False) -> int:
    col = _get_collection()

    if force:
        _client.delete_collection(COLLECTION)
        col = _get_collection()

    if col.count() > 0 and not force:
        return col.count()

    docs, ids, metas = [], [], []
    files = (
        glob.glob(os.path.join(DATA_DIR, "*.txt")) +
        glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    )

    for filepath in files:
        filename = os.path.basename(filepath)
        if filepath.endswith(".pdf"):
            text = _read_pdf(filepath)
        else:
            with open(filepath, encoding="utf-8") as f:
                text = f.read()

        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(chunk)
            ids.append(f"{filename}_{i}")
            metas.append({"source": filename, "chunk": i})

    if docs:
        col.add(documents=docs, ids=ids, metadatas=metas)

    return len(docs)


# ──────────────────────────────────────────────
# Recuperación
# ──────────────────────────────────────────────

def retrieve(query: str, top_k: int = TOP_K) -> str:
    col = _get_collection()

    if col.count() == 0:
        return ""

    results = col.query(
        query_texts=[query],
        n_results=min(top_k, col.count()),
    )

    fragments = results.get("documents", [[]])[0]
    sources   = [m.get("source", "") for m in results.get("metadatas", [[]])[0]]

    if not fragments:
        return ""

    context_parts = []
    for frag, src in zip(fragments, sources):
        context_parts.append(f"[Fuente: {src}]\n{frag}")

    return "\n\n---\n\n".join(context_parts)


# ──────────────────────────────────────────────
# Inicialización al importar
# ──────────────────────────────────────────────

_indexed = build_index()
print(f"[RAG] Índice listo — {_indexed} fragmentos desde {DATA_DIR}")