import os
import json
import numpy as np
import faiss
import nltk
from sentence_transformers import SentenceTransformer

# Ensure the sentence tokenizer is available
nltk.download('punkt', quiet=True)

MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_PATH = "data/indexes/nagaland_dense.index"
DATA_PATH = "data/raw/nagaland_pages.jsonl"

class DenseRetriever:
    def __init__(self):
        print(f"🔄 Loading Dense Model: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.documents = []  # Stores context-aware chunks

        self._load_or_build_index()

    def _load_or_build_index(self):
        """
        Loads the index from disk or builds a new one using sliding-window chunking.
        """
        os.makedirs("data/indexes", exist_ok=True)

        # 1. Load Raw Data
        raw_pages = []
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    raw_pages.append(data["text"])
        else:
            print(f"⚠️ Warning: Data file not found at {DATA_PATH}")
            return

        # 2. Context-Aware Chunking (The 'Middle Ground' Logic)
        print("✂️ Applying Context-Aware Chunking (3-sentence windows)...")
        new_docs = []
        for page in raw_pages:
            sentences = nltk.sent_tokenize(page)
            # Create overlapping windows of 3 sentences to keep context intact
            for i in range(0, len(sentences), 2): 
                window = sentences[i : i + 3]
                chunk = " ".join(window).strip()
                # Only keep chunks with enough substance (prevents "too short" snippets)
                if len(chunk) > 100:
                    new_docs.append(chunk)
        
        self.documents = new_docs

        # 3. Check if we need to rebuild
        # We rebuild if the index is missing OR if we want to refresh the chunking logic
        if os.path.exists(INDEX_PATH):
            print("📁 Loading existing Dense Index...")
            self.index = faiss.read_index(INDEX_PATH)
            
            # For your specific improvement, we need to ensure the index 
            # matches the new 3-sentence chunking logic.
            if len(self.documents) != self.index.ntotal:
                print("🔄 Chunking logic changed. Rebuilding index for precision...")
                self._build_and_save_index()
        else:
            self._build_and_save_index()

    def _build_and_save_index(self):
        """Helper to encode documents and save the FAISS index."""
        print(f"🚀 Building NEW Dense Index with {len(self.documents)} meaningful chunks...")
        embeddings = self.model.encode(
            self.documents, show_progress_bar=True, convert_to_numpy=True)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

        faiss.write_index(self.index, INDEX_PATH)
        print(f"✅ Re-indexed with better context! Saved to {INDEX_PATH}")

    def search(self, query, top_k=3):
        """Search the index for the most relevant 3-sentence chunks."""
        if self.index is None:
            return []

        query_vector = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(
            query_vector.astype('float32'), top_k)

        results = []
        for i in range(len(indices[0])):
            doc_idx = indices[0][i]
            if doc_idx < len(self.documents):
                # Convert L2 distance to a 0-1 similarity score
                score = 1 / (1 + distances[0][i])
                results.append((score, self.documents[doc_idx]))

        return results

# Singleton instance
_retriever = None

def search_dense(query, top_k=3):
    global _retriever
    if _retriever is None:
        _retriever = DenseRetriever()
    return _retriever.search(query, top_k)