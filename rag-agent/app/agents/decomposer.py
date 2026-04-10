import json
import re
from app.models.llm import call_llm
from app.utils.helpers import load_prompt


def decompose_query(query: str) -> list[str]:
    prompt_template = load_prompt("decomposer.txt")
    prompt = prompt_template.format(query=query)
    response = call_llm(prompt).strip()

    # Robustly extract JSON list from the response using regex
    # This handles cases where the LLM includes markdown (```json) or conversational filler
    match = re.search(r"\[.*\]", response, re.DOTALL)

    if match:
        json_str = match.group(0)
        try:
            sub_queries = json.loads(json_str)
            # Ensure it's a non-empty list of strings
            if isinstance(sub_queries, list) and len(sub_queries) > 0:
                return [str(q).strip() for q in sub_queries]
        except json.JSONDecodeError:
            pass

    # Fallback: if parsing fails or LLM gives plain text, just return the original query
    return [query]
