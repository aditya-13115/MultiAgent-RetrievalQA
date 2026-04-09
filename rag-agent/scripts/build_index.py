import os
import sys
from tqdm import tqdm
import numpy as np

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import embed_texts
from app.ingestion.indexer import build_faiss_index

def main():
    # 1. Configuration [cite: 240, 248]
    corpus_pdf = "data/raw/healthcare_ai_corpus_v2.pdf"
    index_path = "data/index"
    batch_size = 32  # Adjust based on your GPU/CPU memory
    
    if not os.path.exists(corpus_pdf):
        print(f" Error: {corpus_pdf} not found. Ensure the file is in data/raw/")
        return

    # 2. Loading & Fetching [cite: 254, 259]
    # This now uses the PyMuPDF loader to find all 21 articles
    docs = load_documents(corpus_pdf)
    if not docs:
        print(" No documents were loaded. Check your loader logic.")
        return

    # 3. Chunking [cite: 260]
    print("\n--- Chunking Started ---")
    chunks = []
    for doc in tqdm(docs, desc="Splitting documents into chunks"):
        chunks.extend(chunk_documents([doc]))
    print(f"Chunking Done: {len(chunks)} chunks created.\n")

    # 4. Embedding with tqdm [cite: 260]
    print("--- Embedding Process Started ---")
    texts = [c["text"] for c in chunks]
    all_embeddings = []

    # Process in batches to show progress and manage memory
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating BGE Embeddings"):
        batch_texts = texts[i : i + batch_size]
        batch_embeddings = embed_texts(batch_texts)
        all_embeddings.extend(batch_embeddings)
    
    # Convert list to numpy array for FAISS
    all_embeddings = np.array(all_embeddings).astype('float32')
    print(f"Embedding Done: {len(all_embeddings)} vectors generated.\n")

    # 5. Indexing [cite: 260]
    print("--- FAISS Indexing Started ---")
    os.makedirs(index_path, exist_ok=True)
    build_faiss_index(all_embeddings, chunks, index_path)
    print(f"PIPELINE COMPLETE: Index saved to {index_path}\n")

if __name__ == "__main__":
    main()