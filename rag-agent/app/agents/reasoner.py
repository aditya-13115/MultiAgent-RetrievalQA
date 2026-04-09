from app.models.llm import call_llm
from app.utils.helpers import load_prompt
import re


# -------------------------
# CLEAN DOC ID
# -------------------------
def clean_doc_id(doc_id: str) -> str:
    if not doc_id:
        return "Art. 00"

    doc_id = doc_id.replace("\u202f", " ").replace("\xa0", " ")

    match = re.search(r'(\d+)', doc_id)
    if match:
        num = int(match.group(1))
        return f"Art. {str(num).zfill(2)}"

    return "Art. 00"


# -------------------------
# GENERATE ANSWER
# -------------------------
def generate_answer(query: str, retrieved_docs: list) -> str:
    context_str = ""

    for doc in retrieved_docs:
        doc_id = clean_doc_id(doc["metadata"].get("doc_id", ""))
        title = doc["metadata"].get("title", "Unknown Title")
        text = doc["text"]

        context_str += f"\n--- [{doc_id}] {title} ---\n{text}\n"

    prompt_template = load_prompt("reasoner.txt")

    prompt = f"{prompt_template}\n\nQuery:\n{query}\n\nContext:\n{context_str.strip()}"

    # IMPORTANT: number extraction enforcement
    prompt += """
    
IMPORTANT:
- Extract ALL numbers and percentages
- If multiple numbers exist → choose the one directly answering the question
- Missing numbers = WRONG answer
"""

    return call_llm(prompt)