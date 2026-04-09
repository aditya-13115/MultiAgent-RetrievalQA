import os
import sys

# Ensure the app directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.retriever import BaseRetriever
from app.memory.chat_memory import ChatMemory
from app.agents.orchestrator import Orchestrator
from app.constants import INDEX_DIR

def run_test(q1, q2=None):
    # Initialize fresh system for each test
    r = BaseRetriever(INDEX_DIR)
    memory = ChatMemory()
    agent = Orchestrator(r, memory)

    def print_agent_traces(query, result, step_name):
        print(f"\n{'='*20} {step_name} {'='*20}")
        print(f"USER QUERY: {query}")
        
        # 1. Router Trace
        print(f"\n[AGENT: ROUTER] -> Classification: {result.get('route')}")

        # 2. Rewriter Trace
        print(f"\n[AGENT: REWRITER] -> Standalone Query: {result.get('rewritten_query')}")

        # 3. Decomposer Trace
        print(f"\n[AGENT: DECOMPOSER] -> Sub-Queries: {result.get('sub_queries')}")

        # 4. Reasoner Trace (Chain-of-Thought)
        print("\n" + "-"*15 + " AGENT: REASONER (CHAIN-OF-THOUGHT) " + "-"*15)
        # This fulfills the 'visible reasoning trace' requirement
        print(result.get('reasoner_output', 'No reasoning generated.'))

        # 5. Critic Trace (Bonus Agent)
        if result.get('critic_output'):
            print("\n" + "-"*15 + " AGENT: CRITIC (VERIFICATION) " + "-"*15)
            print(result.get('critic_output'))

        print("\n" + "-"*15 + " FINAL CONSOLIDATED ANSWER " + "-"*15)
        print(result.get("answer"))
        print(f"{'='*50}\n")

    # --- EXECUTE QUERY 1 ---
    result1 = agent.process_query(q1)
    print_agent_traces(q1, result1, "TEST 1: FACTUAL")

    # --- EXECUTE QUERY 2 (FOLLOW-UP) ---
    if q2:
        result2 = agent.process_query(q2)
        print_agent_traces(q2, result2, "TEST 2: FOLLOW-UP")


if __name__ == "__main__":
    # TEST 1 — Factual & Multi-hop
    # Should demonstrate Query Decomposition and bridging Articles 13 & 14
    #run_test("What are challenges and progress in AI drug discovery?")

    # TEST 2 — Conversation Context
    # Should demonstrate the Rewriter turning "What about regulation?" into a standalone query
    run_test(
        "What are challenges in AI drug discovery?",
       "What about regulation?"
   )

    # TEST 3 — Out of Scope
    # Should demonstrate the Router identifying a non-healthcare query
    #run_test("Who is Elon Musk?")