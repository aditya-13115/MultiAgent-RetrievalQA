from app.models.llm import call_llm
from app.utils.helpers import load_prompt

def generate_answer(query: str, retrieved_docs: list) -> str:
    context_str = ""
    for doc in retrieved_docs:
        doc_id = doc["metadata"].get("doc_id", "Unknown")
        title = doc["metadata"].get("title", "Unknown Title")
        text = doc["text"]
        context_str += f"\n--- [{doc_id}] {title} ---\n{text}\n"
        
    prompt_template = load_prompt("reasoner.txt")
    
    # Notice: Your reasoner.txt does not have explicitly defined {query} and {context}
    # brackets, so we append them cleanly to the end of your prompt template.
    prompt = f"{prompt_template}\n\nUSER QUERY:\n{query}\n\nRETRIEVED CONTEXT:\n{context_str.strip()}"
    
    return call_llm(prompt)