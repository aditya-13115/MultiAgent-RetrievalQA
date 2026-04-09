# app/retrieval/hybrid.py
from app.retrieval.retriever import BaseRetriever
from app.retrieval.reranker import rerank_documents

def hybrid_search(query, retriever: BaseRetriever, top_k=5, alpha=0.6):
    """
    Combines dense and sparse retrieval, applies RRF, and reranks the output.
    """
    # 1. Fetch wider initial pools (e.g., top_k * 2)
    pool_size = top_k * 3
    dense_results = retriever.dense_search(query, top_k=pool_size)
    sparse_results = retriever.sparse_search(query, top_k=pool_size)
    
    # 2. Combine using Reciprocal Rank Fusion (RRF)
    combined_docs = {}
    
    def add_to_fusion(results, weight):
        for rank, res in enumerate(results):
            chunk_id = res["doc"]["metadata"]["chunk_id"]
            if chunk_id not in combined_docs:
                combined_docs[chunk_id] = {"doc": res["doc"], "rrf_score": 0.0}
            
            # RRF formula: 1 / (constant + rank)
            combined_docs[chunk_id]["rrf_score"] += weight * (1.0 / (5 + rank))
            
    # Apply fusion weights (alpha controls balance between dense/sparse)
    add_to_fusion(dense_results, alpha)
    add_to_fusion(sparse_results, 1.0 - alpha)
    
    # Sort by fused score
    fused_list = sorted(list(combined_docs.values()), key=lambda x: x["rrf_score"], reverse=True)
    
    # 3. Rerank the top candidates
    final_results = rerank_documents(query, fused_list[:pool_size], top_k=top_k)
    
    # Extract just the document dictionaries to return to the agents
    return [res["doc"] for res in final_results]