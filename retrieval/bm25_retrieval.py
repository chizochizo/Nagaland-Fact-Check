import json
import os
# This pulls the class you just showed me from the index file
from retrieval.bm25_index import BM25Retriever

DATA_PATH = "data/raw/nagaland_pages.jsonl"


def load_documents(path):
    documents = []
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "text" in data:
                    documents.append(data["text"])
            except:
                continue
    return documents


# Initialize the global instance once for the whole app
_docs = load_documents(DATA_PATH)
_bm25_instance = BM25Retriever(_docs) if _docs else None


def search_bm25(query, top_k=3):
    """
    The function that hybrid_retrieval.py and pipeline.py need.
    """
    if _bm25_instance:
        return _bm25_instance.search(query, top_k)
    return []
