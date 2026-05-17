"""
Test du RAG hybride BM25 + FAISS.
Usage: uv run python scripts/test_rag.py
"""
from app.rag.retriever import retriever

QUERIES = [
    ("colis perdu réclamation indemnisation",         "perte de colis"),
    ("SLA délai traitement courrier réclamation",     "SLA / réclamation"),
    ("lettre recommandée indemnisation type envoi",   "courrier / indemnisation"),
    ("enquête transport suivi bloqué 5 jours",        "actions conseiller"),
    ("client premium escalade superviseur",           "escalade"),
]

def run():
    print("=== TEST RAG HYBRIDE ===\n")
    for query, expected_topic in QUERIES:
        print(f"QUERY  : {query}")
        print(f"ATTENDU: {expected_topic}")
        try:
            docs = retriever.retrieve(query, top_k=2)
            for i, doc in enumerate(docs):
                src     = doc["metadata"]["source"]
                section = doc["metadata"]["section"]
                score   = doc["score"]
                preview = doc["text"][:120].replace("\n", " ")
                print(f"  [{i+1}] {src} | {section} | score={score:.4f}")
                print(f"       {preview}...")
        except Exception as e:
            print(f"  ERREUR: {e}")
        print()

if __name__ == "__main__":
    run()