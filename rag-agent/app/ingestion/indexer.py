import faiss
import numpy as np
import pickle


def build_faiss_index(embeddings, chunks, save_path):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)

    index.add(np.array(embeddings))

    faiss.write_index(index, f"{save_path}/faiss.index")

    with open(f"{save_path}/metadata.pkl", "wb") as f:
        pickle.dump(chunks, f)
