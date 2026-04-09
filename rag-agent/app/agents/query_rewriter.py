import re
from app.models.llm import call_llm
from app.utils.helpers import load_prompt


def rewrite_query(query: str, history: str) -> str:
    prompt_template = load_prompt("rewriter.txt")
    prompt = prompt_template.format(history=history, query=query)

    raw_output = call_llm(prompt)

    # ✅ REMOVE ALL <think> blocks completely
    clean_query = re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL).strip()

    return clean_query