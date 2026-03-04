import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_PATH = "data/indexes/nagaland_dense.index"
DATA_PATH = "data/raw/nagaland_pages.jsonl"


class DenseRetriever:
    def __init__(self):
        # 1. Load the model (CPU-friendly)
        print(f"🔄 Loading Dense Model: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.documents = []

        # 2. Initialize the index
        self._load_or_build_index()

    def _load_or_build_index(self):
        # Ensure directory exists
        os.makedirs("data/indexes", exist_ok=True)

        # Load raw documents first
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                self.documents.append(data["text"])

        if os.path.exists(INDEX_PATH):
            print("📁 Loading existing Dense Index from disk...")
            self.index = faiss.read_index(INDEX_PATH)
        else:
            print("🚀 Building NEW Dense Index (this may take a minute on CPU)...")
            # Convert texts to vectors in batches to save RAM
            embeddings = self.model.encode(
                self.documents, show_progress_bar=True, convert_to_numpy=True)

            # FAISS Index (FlatL2 is precise for smaller datasets)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))

            # Save to disk for next time
            faiss.write_index(self.index, INDEX_PATH)
            print(f"✅ Dense Index saved to {INDEX_PATH}")

    def search(self, query, top_k=3):
        # Convert query to vector
        query_vector = self.model.encode([query], convert_to_numpy=True)

        # Search the index
        distances, indices = self.index.search(
            query_vector.astype('float32'), top_k)

        results = []
        for i in range(len(indices[0])):
            doc_idx = indices[0][i]
            # FAISS distance for L2 is 'lower is better'
            # We convert it to a similarity score for easier hybrid merging later
            score = 1 / (1 + distances[0][i])
            results.append((score, self.documents[doc_idx]))

        return results


# Singleton instance for the system
_retriever = None


def search_dense(query, top_k=3):
    global _retriever
    if _retriever is None:
        _retriever = DenseRetriever()
    return _retriever.search(query, top_k)
