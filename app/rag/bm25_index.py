import os
import json

from whoosh import index, scoring
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser, OrGroup


class BM25DiskIndex:
    """
    Persistent BM25 index backed by Whoosh on disk.
    Optimized for large JSONL corpora (CSV chunks or PDF chunks).

    Key fixes vs previous version:
    - Single commit with limitmb to avoid segment explosion
    - OrGroup parser for better recall on multi-word DVF queries
      (e.g. "prix médian appartement Paris 2022" → OR instead of AND)
    """

    def __init__(self, chunks_path: str, index_dir: str):
        self.chunks_path = chunks_path
        self.index_dir = index_dir

        os.makedirs(index_dir, exist_ok=True)

        if not index.exists_in(index_dir):
            self._build_index()

        self.ix = index.open_dir(index_dir)

    def _build_index(self):
        schema = Schema(
            id=ID(stored=True, unique=True),
            content=TEXT(stored=False),
            source=TEXT(stored=False),
            section=TEXT(stored=False),
        )

        ix = index.create_in(self.index_dir, schema)

        # Single writer with high memory limit → one large segment instead of thousands
        writer = ix.writer(limitmb=512, procs=1)

        count = 0
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                chunk = json.loads(line)
                metadata = chunk.get("metadata", {})
                writer.add_document(
                    id=str(chunk["id"]),
                    content=chunk["text"],
                    source=metadata.get("source", ""),
                    section=metadata.get("section", ""),
                )
                count += 1
                if count % 10_000 == 0:
                    print(f"  BM25 indexing: {count:,} chunks...")

        writer.commit()
        print(f"BM25 index built: {count:,} documents in {self.index_dir}")

    def search(self, query: str, top_k: int = 50) -> list[dict]:
        """
        Returns list of {"id": int, "score": float}.
        Uses OrGroup so partial keyword matches still return results —
        critical for DVF queries that mix domain terms + location + year.
        """
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            parser = MultifieldParser(
                ["content", "source", "section"], self.ix.schema, group=OrGroup
            )
            q = parser.parse(query)
            results = searcher.search(q, limit=top_k)
            return [
                {"id": int(r["id"]), "score": float(r.score)}
                for r in results
            ]


class BM25InMemoryIndex:
    """
    In-memory BM25 using rank_bm25.
    Use only for small corpora (< 50k chunks) or testing.
    """

    def __init__(self, chunks_dict: dict):
        from rank_bm25 import BM25Okapi  # lazy import — optional dependency

        self.chunk_ids = list(chunks_dict.keys())
        self.texts = [chunks_dict[cid]["text"] for cid in self.chunk_ids]
        tokenized_corpus = [text.split() for text in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 50) -> list[dict]:
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(
            zip(self.chunk_ids, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"id": doc_id, "score": float(score)}
            for doc_id, score in ranked[:top_k]
        ]
