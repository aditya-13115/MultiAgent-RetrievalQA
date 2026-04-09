from app.agents.router import route_query
from app.agents.query_rewriter import rewrite_query
from app.agents.decomposer import decompose_query
from app.agents.reasoner import generate_answer
from app.agents.critic import evaluate_answer
from app.retrieval.hybrid import hybrid_search
import re


# -------------------------
# CLEAN DOC ID
# -------------------------
def clean_doc_id(doc_id: str) -> str:
    if not doc_id:
        return "Art. 00"

    doc_id = doc_id.replace("\u202f", " ").replace("\xa0", " ")

    match = re.search(r"(\d+)", doc_id)
    if match:
        num = int(match.group(1))
        return f"Art. {str(num).zfill(2)}"

    return "Art. 00"


# -------------------------
# NORMALIZE ANSWER
# -------------------------
def normalize_answer(ans: str) -> str:
    if not ans:
        return ""

    ans = ans.replace("\u202f", " ")
    ans = ans.replace("–", "-")

    ans = re.sub(r"(\d)\s*%", r"\1%", ans)
    ans = re.sub(r"\s+", " ", ans)

    return ans.strip()


# -------------------------
# EXTRACT USED DOCS
# -------------------------
def extract_used_docs(text: str):
    text = text.replace("\u202f", " ").replace("\xa0", " ")

    matches = re.findall(r"Art\.\s*(\d{1,2})", text)

    cleaned = []
    for m in matches:
        cleaned.append(f"[Art. {str(int(m)).zfill(2)}]")

    return sorted(list(set(cleaned)))


class Orchestrator:
    def __init__(self, retriever, memory):
        self.retriever = retriever
        self.memory = memory

    def process_query(self, user_query: str) -> dict:
        history_str = self.memory.get_history_string()

        # -------------------------
        # 1. ROUTER
        # -------------------------
        route = route_query(user_query, history_str)
        if len(self.memory.history) == 0 and route == "follow_up":
            route = "factual"

        # -------------------------
        # 2. REWRITE (if needed)
        # -------------------------
        current_query = user_query
        if route == "follow_up":
            current_query = rewrite_query(user_query, history_str)

        # -------------------------
        # 3. DECOMPOSE
        # -------------------------
        sub_queries = decompose_query(current_query)

        # -------------------------
        # 4. RETRIEVAL
        # -------------------------
        all_docs = []
        seen_chunks = set()

        for sq in sub_queries:
            docs = hybrid_search(sq, self.retriever, top_k=5, alpha=0.5)

            for doc in docs:
                cid = doc.get("metadata", {}).get("chunk_id")

                if cid and cid not in seen_chunks:
                    seen_chunks.add(cid)

                    # CLEAN DOC ID HERE
                    doc["metadata"]["doc_id"] = clean_doc_id(
                        doc["metadata"].get("doc_id", "")
                    )

                    all_docs.append(doc)
            # ✅ FALLBACK (ADD THIS HERE)
        if not all_docs:
            all_docs = self.retriever.dense_search(current_query, top_k=8)

        final_context = all_docs[:8]

        # -------------------------
        # 5. REASONER
        # -------------------------
        reasoner_output = generate_answer(current_query, final_context)

        reasoner_output = re.sub(
            r"<think>.*?</think>", "", reasoner_output, flags=re.DOTALL
        ).strip()

        # -------------------------
        # 6. EXTRACT USED DOCS
        # -------------------------
        used_docs = extract_used_docs(reasoner_output)

        #
        #  STRICT: ONLY USED DOCS
        final_docs = used_docs if used_docs else []

        # -------------------------
        # 7. CRITIC
        # -------------------------
        critic_output = evaluate_answer(current_query, reasoner_output, final_context)

        # -------------------------
        # 8. FINAL ANSWER
        # -------------------------
        try:
            if "FINAL ANSWER:" in reasoner_output:
                final_answer_only = (
                    reasoner_output.split("FINAL ANSWER:")[-1]
                    .split("CITATIONS:")[0]
                    .strip()
                )
            else:
                final_answer_only = reasoner_output.strip()

        except:
            final_answer_only = ""

        final_answer_only = normalize_answer(final_answer_only)
        # SAFETY FIX
        if not final_answer_only:
            final_answer_only = reasoner_output.strip()

        # -------------------------
        # 9. MEMORY
        # -------------------------
        self.memory.add_interaction(user_query, final_answer_only)

        return {
            "route": route,
            "rewritten_query": current_query,
            "sub_queries": sub_queries,
            "retrieved_docs": final_docs,
            "reasoner_output": reasoner_output,
            "critic_output": critic_output,
            "answer": final_answer_only,
        }
