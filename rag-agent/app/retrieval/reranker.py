# app/retrieval/reranker.py
from sentence_transformers import CrossEncoder

# We use a fast, effective cross-encoder from HuggingFace
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_documents(query, documents, top_k=5):
    if not documents:
        return []
    
    # Prepare pairs of (query, chunk_text) for the cross-encoder
    pairs = [[query, item["doc"]["text"]] for item in documents]
    
    # Predict relevance scores
    scores = reranker_model.predict(pairs)
    
    # Attach scores and sort
    for i, doc in enumerate(documents):
        doc["rerank_score"] = float(scores[i])
        
    reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]