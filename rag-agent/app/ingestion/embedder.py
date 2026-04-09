from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en")


def embed_texts(texts):
    return model.encode(texts, normalize_embeddings=True)
