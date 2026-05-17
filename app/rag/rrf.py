from collections import defaultdict


def reciprocal_rank_fusion(results: dict[str, list], k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion across multiple retrievers.

    Args:
        results: dict mapping retriever_name → list of {"id", "score", "source"} dicts
        k:       RRF constant (default 60, standard in literature)

    Returns:
        Sorted list of {"id", "score", "sources"} where sources tracks ALL retrievers
        that found this doc — critical for correct JSONL routing in MultiIndexHybridRAG.

    Fix vs previous version:
        - "source" was overwritten on first-seen; now we track ALL sources per doc.
        - When a doc appears in both small and big retrievers, we keep both sources
          so the caller can decide which JSONL to read from (priority: small > big).
    """
    scores: dict = {}
    sources: dict[int, set] = defaultdict(set)

    for retriever_name, docs in results.items():
        for rank, doc in enumerate(docs):
            doc_id = doc["id"]
            doc_source = doc.get("source", retriever_name)

            if doc_id not in scores:
                scores[doc_id] = 0.0

            scores[doc_id] += 1.0 / (k + rank + 1)
            sources[doc_id].add(doc_source)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {
            "id": doc_id,
            "score": score,
            # Primary source = small if available (more precise), else big
            "source": "small" if "small" in sources[doc_id] else next(iter(sources[doc_id])),
            "all_sources": list(sources[doc_id]),
        }
        for doc_id, score in ranked
    ]
