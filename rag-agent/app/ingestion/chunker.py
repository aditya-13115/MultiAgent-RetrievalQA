from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.constants import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["text"])
        for i, chunk in enumerate(splits):
            chunks.append({
                "text": chunk,
                "metadata": {
                    **doc["metadata"],
                    "chunk_id": f"{doc['metadata']['doc_id']}_{i}"
                }
            })
    return chunks