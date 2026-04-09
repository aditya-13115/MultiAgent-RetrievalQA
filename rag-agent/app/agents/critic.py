import re
from app.models.llm import call_llm
from app.utils.helpers import load_prompt


def evaluate_answer(query: str, answer: str, retrieved_docs: list) -> str:
    context_str = ""
    for doc in retrieved_docs:
        doc_id = doc["metadata"].get("doc_id", "Unknown")
        context_str += f"[{doc_id}]: {doc['text']}\n"

    prompt_template = load_prompt("critic.txt")
    prompt = prompt_template.format(
        query=query, answer=answer, context=context_str.strip()
    )

    raw_output = call_llm(prompt)

    # REMOVE <think> completely
    clean_output = re.sub(
        r"<think>.*?</think>", "", raw_output, flags=re.DOTALL
    ).strip()

    return clean_output
