# app/retrieval/retriever.py
import faiss
import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from app.ingestion.embedder import embed_texts


class BaseRetriever:
    def __init__(self, index_dir):
        # Load Dense FAISS Index
        self.index = faiss.read_index(f"{index_dir}/faiss.index")

        # Load Metadata (Chunks)
        with open(f"{index_dir}/metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

        # Setup Sparse BM25 Index
        tokenized_corpus = [doc["text"].lower().split() for doc in self.metadata]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def dense_search(self, query, top_k=12):
        """Semantic search using embeddings."""
        query_embedding = embed_texts([query])
        distances, indices = self.index.search(np.array(query_embedding), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata) and idx != -1:
                results.append(
                    {"doc": self.metadata[idx], "score": float(distances[0][i])}
                )
        return results

    def sparse_search(self, query, top_k=12):
        """Keyword-based search using BM25."""
        tokenized_query = query.lower().split()
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(doc_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({"doc": self.metadata[idx], "score": float(doc_scores[idx])})
        return results
