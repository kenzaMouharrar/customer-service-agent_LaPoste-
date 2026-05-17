import numpy as np


class FAISSIndexWrapper:
    """
    Wraps a raw FAISS index with chunk ID mapping and safe embedding handling.
    """

    def __init__(self, faiss_index, chunk_ids: list):
        self.index = faiss_index
        self.chunk_ids = chunk_ids

        # Detect desync at load time — fail fast with a clear message
        n_faiss = self.index.ntotal
        n_ids   = len(self.chunk_ids)
        if n_faiss != n_ids:
            raise ValueError(
                f"FAISSIndexWrapper: FAISS index has {n_faiss} vectors "
                f"but chunk_ids has {n_ids} entries. "
                f"The index and the JSONL file are out of sync — "
                f"rebuild one or both."
            )

    def search(self, query_embedding, top_k: int = 20) -> list[tuple]:
        """
        Returns list of (chunk_id, score) tuples.
        Accepts both (dim,) and (1, dim) shaped embeddings.
        """
        emb = np.array(query_embedding, dtype=np.float32)

        # Guard: FAISS requires shape (1, dim)
        if emb.ndim == 1:
            emb = emb.reshape(1, -1)
        elif emb.ndim == 2 and emb.shape[0] != 1:
            raise ValueError(
                f"FAISSIndexWrapper.search: expected single query, got shape {emb.shape}"
            )

        scores, indices = self.index.search(emb, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            # Bounds check — should never trigger after __init__ sync check,
            # but protects against subtle race conditions or partial reloads
            if idx >= len(self.chunk_ids):
                print(f"[FAISSIndexWrapper] Warning: idx={idx} out of range "
                      f"(chunk_ids len={len(self.chunk_ids)}), skipping.")
                continue
            chunk_id = self.chunk_ids[idx]
            results.append((chunk_id, float(score)))

        return results
