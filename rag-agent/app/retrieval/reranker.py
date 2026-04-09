# app/retrieval/reranker.py
from sentence_transformers import CrossEncoder

# We use a fast, effective cross-encoder from HuggingFace
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_documents(query, documents, top_k=7):
    if not documents:
        return []

    # Prepare pairs of (query, chunk_text) for the cross-encoder
    pairs = [[query, item["doc"]["text"]] for item in documents]

    # Predict relevance scores
    scores = reranker_model.predict(pairs)

    # keyword overlap calculation
    query_terms = set(query.lower().split())

    # Attach scores and sort
    for i, doc in enumerate(documents):
        text = doc["doc"]["text"].lower()
        # compute keyword overlap
        overlap = sum(1 for t in query_terms if t in text)
        # final score = semantic + keyword boost
        doc["rerank_score"] = float(scores[i]) + 0.1 * overlap

    reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]
