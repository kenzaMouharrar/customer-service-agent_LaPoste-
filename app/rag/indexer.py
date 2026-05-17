"""
Indexation RAG: chunke les fichiers .md et construit les index BM25 + FAISS.

Usage:
    uv run python -m app.rag.indexer
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import faiss
import numpy as np

from app.rag.embedder import embed_texts
from app.rag.bm25_index import BM25DiskIndex

RAG_DOCS_DIR = Path("data/rag_docs")
RUNTIME_DIR = Path("data/runtime/rag")
CHUNKS_JSONL = RUNTIME_DIR / "chunks.jsonl"
CHUNK_IDS_JSON = RUNTIME_DIR / "chunk_ids.json"
FAISS_INDEX_FILE = RUNTIME_DIR / "faiss.index"
BM25_INDEX_DIR = str(RUNTIME_DIR / "bm25")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Reconnaît: ## Titre, # Titre, ou une ligne courte (≤70 chars) terminant par ':'
_SECTION_HEADER = re.compile(
    r"(?m)^(#{1,3}\s+.+|[^\n]{3,70}:)\s*$"
)


def _split_sections(text: str, fallback_title: str) -> list[dict]:
    """Découpe le texte en sections logiques."""
    text = text.replace("\r\n", "\n").strip()
    sections: list[dict] = []
    current_title = fallback_title
    last_pos = 0

    for m in _SECTION_HEADER.finditer(text):
        fragment = text[last_pos : m.start()].strip()
        if fragment:
            sections.append({"section": current_title, "text": fragment})
        current_title = m.group().strip().rstrip(":").lstrip("#").strip()
        last_pos = m.end()

    remainder = text[last_pos:].strip()
    if remainder:
        sections.append({"section": current_title, "text": remainder})

    return sections or [{"section": fallback_title, "text": text}]


def _window_chunks(
    text: str, section: str, source: str, start_id: int
) -> list[dict]:
    """Fenêtres glissantes avec overlap."""
    chunks: list[dict] = []
    pos = 0
    idx = 0

    while pos < len(text):
        end = min(pos + CHUNK_SIZE, len(text))
        fragment = text[pos:end].strip()
        if fragment:
            chunks.append(
                {
                    "id": start_id + idx,
                    "text": fragment,
                    "metadata": {
                        "source": source,
                        "section": section,
                        "chunk_index": idx,
                    },
                }
            )
            idx += 1
        if end == len(text):
            break
        pos += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def chunk_md_files(docs_dir: Path) -> list[dict]:
    """Produit tous les chunks depuis les fichiers .md de docs_dir."""
    all_chunks: list[dict] = []
    chunk_id = 0

    for md_path in sorted(docs_dir.glob("*.md")):
        if md_path.stat().st_size == 0:
            print(f"  Ignoré (vide): {md_path.name}")
            continue

        text = md_path.read_text(encoding="utf-8")
        source = md_path.name
        sections = _split_sections(text, source.replace(".md", ""))

        file_chunks: list[dict] = []
        for sec in sections:
            new = _window_chunks(sec["text"], sec["section"], source, chunk_id)
            file_chunks.extend(new)
            chunk_id += len(new)

        all_chunks.extend(file_chunks)
        print(f"  {source}: {len(file_chunks)} chunks")

    return all_chunks


def build_indexes(chunks: list[dict]) -> None:
    """Construit et persiste les index FAISS et BM25."""
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    # Réinitialise le dossier BM25 pour forcer la reconstruction
    bm25_dir = Path(BM25_INDEX_DIR)
    if bm25_dir.exists():
        shutil.rmtree(bm25_dir)

    # Écrit le JSONL
    with CHUNKS_JSONL.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"\nChunks écrits: {len(chunks)} → {CHUNKS_JSONL}")

    # Mapping ID
    with CHUNK_IDS_JSON.open("w", encoding="utf-8") as f:
        json.dump([c["id"] for c in chunks], f)

    # Embeddings + FAISS IndexFlatIP (vecteurs déjà normalisés = cosine)
    texts = [c["text"] for c in chunks]
    print(f"Calcul des embeddings ({len(texts)} chunks)...")
    embeddings = embed_texts(texts)  # déjà normalisés par l'embedder

    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim)
    faiss_index.add(embeddings)
    faiss.write_index(faiss_index, str(FAISS_INDEX_FILE))
    print(f"Index FAISS: {faiss_index.ntotal} vecteurs → {FAISS_INDEX_FILE}")

    # BM25 Whoosh
    print("Construction de l'index BM25...")
    BM25DiskIndex(str(CHUNKS_JSONL), BM25_INDEX_DIR)
    print(f"Index BM25 → {BM25_INDEX_DIR}")


def main() -> None:
    print("=== Indexation RAG - La Poste ===")
    print(f"Source: {RAG_DOCS_DIR.resolve()}\n")

    chunks = chunk_md_files(RAG_DOCS_DIR)
    if not chunks:
        print("Aucun chunk produit. Vérifiez data/rag_docs/")
        return

    print(f"\nTotal: {len(chunks)} chunks")
    build_indexes(chunks)
    print("\n✓ Indexation terminée.")


if __name__ == "__main__":
    main()
