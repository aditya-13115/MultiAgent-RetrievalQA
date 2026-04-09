import json
import os
import sys

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.retriever import BaseRetriever
from app.memory.chat_memory import ChatMemory
from app.agents.orchestrator import Orchestrator
from app.constants import INDEX_DIR
from eval.scorer import final_score, llm_judge_full


# =========================
# LOAD QUESTIONS
# =========================
def load_questions(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} questions")
    return data


# -------------------------
# DEBUG PRINT (FIXED)
# -------------------------
def print_debug(q, result, answer, score, rubric):
    print("\n" + "=" * 60)
    print(f" {q['id']}")
    print("=" * 60)

    print("\n QUESTION:")
    print(q["question"])

    print("\n ROUTE:", result.get("route"))
    print("\n SUB-QUERIES:", result.get("sub_queries"))

    # ONLY USED DOCS (FIX)
    print("\n USED CITATIONS:")
    used_docs = result.get("retrieved_docs", [])
    print(used_docs if used_docs else "None")

    print("\n MODEL ANSWER:")
    print(answer if answer else " EMPTY")

    print("\n EXPECTED ANSWER:")
    print(q["answer"])

    print(f"\n SCORE: {score:.2f}/10")

    print("\n RUBRIC:")
    print(rubric)

    print("=" * 60 + "\n")


# =========================
# MAIN EVAL LOOP
# =========================
def main():
    questions = load_questions("eval/questions.json")
    if not questions:
        return

    retriever = BaseRetriever(INDEX_DIR)

    results = []
    print("\nSTARTING EVAL RUN\n")

    for q in questions:
        memory = ChatMemory()
        agent = Orchestrator(retriever, memory)

        try:
            result = agent.process_query(q["question"])
            answer = result.get("answer", "")

            #  ADD: pass reasoning also
            reasoning = result.get("reasoner_output", "")

            #  UPDATED: better scoring using reasoning + answer
            score = final_score(answer, q["answer"])
            rubric = llm_judge_full(
                reasoning + "\n\nFINAL ANSWER:\n" + answer,
                q["answer"]
            )

            print_debug(q, result, answer, score, rubric)

            results.append({
            "id": q["id"],
            "question": q["question"],
            "model_answer": answer,
            "expected_answer": q["answer"],
            "used_docs": result.get("retrieved_docs", []),
            "score": score,
            "rubric": rubric
        })

        except Exception as e:
            print(f"ERROR in {q['id']}: {e}")

    # =========================
    # SAVE RESULTS
    # =========================
    os.makedirs("eval", exist_ok=True)

    with open("eval/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # =========================
    # FINAL SCORE
    # =========================
    valid = [r["score"] for r in results if "score" in r]
    avg = sum(valid) / len(valid) if valid else 0

    print("\n" + "=" * 60)
    print(f" FINAL AVG SCORE: {avg:.2f}/10")
    print("=" * 60)


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    main()