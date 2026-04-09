from app.models.llm import call_llm
from app.utils.helpers import load_prompt
import re


def route_query(query: str, history: str) -> str:
    prompt_template = load_prompt("router.txt")
    prompt = prompt_template.format(history=history, query=query)

    response = call_llm(prompt).strip().lower()

    # CLEAN response (remove punctuation, spaces)
    response = re.sub(r"[^a-z_]", " ", response)
    tokens = response.split()

    # STRICT MATCHING
    if "out_of_scope" in tokens:
        return "out_of_scope"
    elif "follow_up" in tokens:
        return "follow_up"
    elif "factual" in tokens:
        return "factual"

    # fallback safety
    return "factual"
