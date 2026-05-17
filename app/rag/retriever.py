"""
HybridMarkdownRetriever: BM25 + FAISS + RRF sur les docs Markdown La Poste.
Lazy-loaded: les index ne sont chargés qu'au premier appel à retrieve().
"""
from __future__ import annotations

import json
from pathlib import Path

import faiss as faiss_lib

from app.rag.bm25_index import BM25DiskIndex
from app.rag.faiss_wrapper import FAISSIndexWrapper
from app.rag.loaders import build_chunk_offset_map, get_chunk_by_id
from app.rag.rrf import reciprocal_rank_fusion

RUNTIME_DIR = Path("data/runtime/rag")
CHUNKS_JSONL = RUNTIME_DIR / "chunks.jsonl"
CHUNK_IDS_JSON = RUNTIME_DIR / "chunk_ids.json"
FAISS_INDEX_FILE = RUNTIME_DIR / "faiss.index"
BM25_INDEX_DIR = str(RUNTIME_DIR / "bm25")


class HybridMarkdownRetriever:
    """Retriever hybride BM25 + FAISS + RRF sur les chunks Markdown."""

    def __init__(self) -> None:
        self._loaded = False
        self._bm25: BM25DiskIndex | None = None
        self._faiss: FAISSIndexWrapper | None = None
        self._offsets: dict | None = None

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        if not FAISS_INDEX_FILE.exists() or not CHUNKS_JSONL.exists():
            raise RuntimeError(
                "Index RAG introuvable. "
                "Lance d'abord: uv run python -m app.rag.indexer"
            )

        with CHUNK_IDS_JSON.open("r", encoding="utf-8") as f:
            chunk_ids = json.load(f)

        raw_index = faiss_lib.read_index(str(FAISS_INDEX_FILE))
        self._faiss = FAISSIndexWrapper(raw_index, chunk_ids)
        self._bm25 = BM25DiskIndex(str(CHUNKS_JSONL), BM25_INDEX_DIR)
        self._offsets = build_chunk_offset_map(str(CHUNKS_JSONL))
        self._loaded = True

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Retourne les top_k chunks les plus pertinents.
        Chaque doc: {id, score, text, metadata: {source, section, chunk_index}}
        """
        self._ensure_loaded()

        from app.rag.embedder import embed_query

        q_emb = embed_query(query)  # (dim,) normalisé L2

        # Recherche sémantique FAISS
        semantic_results = [
            {"id": cid, "score": float(score), "source": "md"}
            for cid, score in self._faiss.search(q_emb, top_k=top_k * 5)
        ]

        # Recherche lexicale BM25
        bm25_results = [
            {"id": int(r["id"]), "score": float(r["score"]), "source": "md"}
            for r in self._bm25.search(query, top_k=top_k * 5)
        ]

        # Fusion RRF
        fused = reciprocal_rank_fusion(
            {"semantic": semantic_results, "bm25": bm25_results}
        )

        # Réhydratation avec le texte et les métadonnées
        final: list[dict] = []
        for doc in fused[:top_k]:
            try:
                chunk = get_chunk_by_id(str(CHUNKS_JSONL), self._offsets, doc["id"])
                final.append(
                    {
                        "id": doc["id"],
                        "score": doc["score"],
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                    }
                )
            except KeyError:
                continue

        return final


# Singleton — chargé au premier retrieve()
retriever = HybridMarkdownRetriever()
