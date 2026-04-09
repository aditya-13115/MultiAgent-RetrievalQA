from app.agents.router import route_query
from app.agents.query_rewriter import rewrite_query
from app.agents.decomposer import decompose_query
from app.agents.reasoner import generate_answer
from app.agents.critic import evaluate_answer
from app.retrieval.hybrid import hybrid_search
import re


class Orchestrator:
    def __init__(self, retriever, memory):
        self.retriever = retriever
        self.memory = memory

    def process_query(self, user_query: str) -> dict:
        history_str = self.memory.get_history_string()

        # -------------------------
        # 1. ROUTER (FIRST STEP)
        # -------------------------
        route = route_query(user_query, history_str)
        if len(self.memory.history) == 0 and route == "follow_up":
            route = "factual"

        # -------------------------
        # ROUTER SAFETY
        # -------------------------
        healthcare_keywords = [
            "clinical", "health", "medical", "fda", "device",
            "trial", "patient", "radiology", "ai", "ethics",
            "regulation", "hospital", "care", "mental"
        ]

        if route == "out_of_scope":
            if any(k in user_query.lower() for k in healthcare_keywords):
                route = "factual"

        # -------------------------
        # 2. OUT-OF-SCOPE HANDLING
        # -------------------------
        if route == "out_of_scope":
            ans = (
                "This query is outside the Healthcare AI domain. "
                "I can only answer questions related to AI in healthcare, "
                "drug discovery, and regulations."
            )

            self.memory.add_interaction(user_query, ans)

            return {
                "route": route,
                "rewritten_query": None,
                "sub_queries": [],
                "retrieved_docs": [],
                "reasoner_output": "Skipped (out_of_scope)",
                "critic_output": None,
                "answer": ans
            }

        # -------------------------
        # 3. FOLLOW-UP REWRITING
        # -------------------------
        current_query = user_query

        if route == "follow_up":
            current_query = rewrite_query(user_query, history_str)
            print(f"Rewritten Query: {current_query}")

        # -------------------------
        # 4. QUERY DECOMPOSITION
        # -------------------------
        sub_queries = decompose_query(current_query)
        print(f"Sub-queries: {sub_queries}")

        # -------------------------
        # 5. HYBRID RETRIEVAL
        # -------------------------
        all_docs = []
        seen_chunks = set()

        for sq in sub_queries:
            docs = hybrid_search(sq, self.retriever, top_k=5, alpha=0.5)

            for doc in docs:
                doc_id = doc.get("metadata", {}).get("doc_id")

                if doc_id and doc_id not in seen_chunks:
                    seen_chunks.add(doc_id)
                    all_docs.append(doc)

        final_context = all_docs[:7]

        # -------------------------
        # 6. REASONER
        # -------------------------
        reasoner_output = generate_answer(current_query, final_context)

        # 🔥 REMOVE <think> (CRITICAL FIX)
        reasoner_output = re.sub(
            r"<think>.*?</think>",
            "",
            reasoner_output,
            flags=re.DOTALL
        ).strip()

        # -------------------------
        # 7. EXTRACT USED DOCS
        # -------------------------
        def extract_used_docs(text):
            matches = re.findall(r'Art\.\s*\d+', text)
            cleaned = [f"[{m.strip()}]" for m in matches]
            return list(set(cleaned))

        used_docs = extract_used_docs(reasoner_output)

        # 🔥 FIX: proper fallback (OUTSIDE return)
        if used_docs:
            final_docs = used_docs
        else:
            final_docs = [
                f"[{d.get('metadata', {}).get('doc_id', 'N/A')}]"
                for d in final_context
            ]

        # -------------------------
        # 8. CRITIC
        # -------------------------
        critic_output = evaluate_answer(current_query, reasoner_output, final_context)

        # -------------------------
        # 9. FINAL ANSWER EXTRACTION
        # -------------------------
        try:
            if "FINAL ANSWER:" in reasoner_output:
                final_answer_only = (
                    reasoner_output
                    .split("FINAL ANSWER:")[-1]
                    .split("CITATIONS:")[0]
                    .strip()
                )
            else:
                final_answer_only = reasoner_output.strip()

        except Exception:
            final_answer_only = (
                "I could not generate a valid answer based on the provided corpus."
            )

        # -------------------------
        # 10. MEMORY UPDATE
        # -------------------------
        self.memory.add_interaction(user_query, final_answer_only)

        # -------------------------
        # 11. FINAL RESPONSE
        # -------------------------
        return {
            "route": route,
            "rewritten_query": current_query,
            "sub_queries": sub_queries,
            "retrieved_docs": final_docs,   # ✅ FIXED
            "reasoner_output": reasoner_output,
            "critic_output": critic_output,
            "answer": final_answer_only
        }