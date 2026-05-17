import json
import faiss


def load_chunks(jsonl_path: str) -> dict:
    """
    Loads ALL chunks into memory as a dict: {id: {text, metadata}}.
    Use only for small corpora or testing — prefer offset-based access for large files.
    """
    chunks = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            chunks[obj["id"]] = {
                "text": obj["text"],
                "metadata": obj.get("metadata", {})
            }
    return chunks



from pathlib import Path

def load_faiss_index(index_path):
    index_path = Path(index_path)
    
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS introuvable : {index_path}")
    
    # C'est directement un fichier .faiss
    if index_path.is_file():
        print(f"[OK] Chargement FAISS : {index_path.name}")
        return faiss.read_index(str(index_path))
    
    # C'est un dossier -> cherche le .faiss dedans
    if index_path.is_dir():
        index_file = next(index_path.glob("*.faiss"), None)
        if index_file is None:
            raise FileNotFoundError(f"Aucun fichier .faiss dans {index_path}")
        print(f"[OK] Chargement FAISS : {index_file.name}")
        return faiss.read_index(str(index_file))



def load_ids_only(jsonl_path: str) -> list:
    """
    Loads only the IDs from a JSONL file, in order.
    Used to map FAISS integer indices → chunk IDs.
    """
    ids = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            ids.append(obj["id"])
    return ids


def build_chunk_offset_map(jsonl_path: str) -> dict:
    """
    Builds a {chunk_id: byte_offset} map for O(1) random access into a JSONL file.
    Much more memory-efficient than loading all chunks into RAM.
    """
    offsets = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            obj = json.loads(line)
            offsets[obj["id"]] = pos
    return offsets


def get_chunk_by_id(jsonl_path: str, offsets: dict, chunk_id) -> dict:
    """
    Fetches a single chunk by ID using the pre-built offset map.
    Seeks directly to the right byte position — no full scan needed.

    Raises KeyError if chunk_id is not in offsets.
    """
    if chunk_id not in offsets:
        raise KeyError(f"chunk_id {chunk_id!r} not found in offset map for {jsonl_path}")

    with open(jsonl_path, "r", encoding="utf-8") as f:
        f.seek(offsets[chunk_id])
        line = f.readline()

    obj = json.loads(line)
    return {
        "text": obj["text"],
        "metadata": obj.get("metadata", {})
    }
