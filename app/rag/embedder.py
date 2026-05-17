"""
Embedder multilingue pour les documents La Poste.
Utilise paraphrase-multilingual-MiniLM-L12-v2 (117 MB, supporte le français).
"""
from __future__ import annotations

import numpy as np

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[Embedder] Chargement du modèle {_MODEL_NAME}...")
        _model = SentenceTransformer(_MODEL_NAME)
        print("[Embedder] Modèle chargé.")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Retourne un tableau (N, dim) float32."""
    model = _get_model()
    return model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=len(texts) > 10,
        normalize_embeddings=True,
    ).astype("float32")


def embed_query(query: str) -> np.ndarray:
    """Retourne un vecteur (dim,) float32, normalisé L2."""
    return embed_texts([query])[0]
