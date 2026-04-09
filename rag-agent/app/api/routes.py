import sys
import os

# FORCE PROJECT ROOT INTO PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from app.api.schemas import QueryRequest, QueryResponse

from app.retrieval.retriever import BaseRetriever
from app.memory.chat_memory import ChatMemory
from app.agents.orchestrator import Orchestrator
from app.constants import INDEX_DIR

app = FastAPI()

# -------------------------
# INIT SYSTEM (GLOBAL)
# -------------------------
retriever = BaseRetriever(INDEX_DIR)
memory = ChatMemory()
agent = Orchestrator(retriever, memory)


# -------------------------
# ROUTES
# -------------------------
@app.get("/")
def home():
    return {"message": "Healthcare AI RAG API is running"}


@app.post("/query", response_model=QueryResponse)
def query_api(req: QueryRequest):
    try:
        result = agent.process_query(req.query)

        return {
            "answer": result.get("answer"),
            "trace": {
                "route": result.get("route"),
                "rewritten_query": result.get("rewritten_query"),
                "sub_queries": result.get("sub_queries"),
                "retrieved_docs": result.get("retrieved_docs"),
                "reasoning": result.get("reasoner_output"),
                "critic": result.get("critic_output"),
            },
        }

    except Exception as e:
        return {
            "answer": "Error occurred",
            "trace": {
                "route": "",
                "rewritten_query": "",
                "sub_queries": [],
                "retrieved_docs": [],
                "reasoning": str(e),
                "critic": None,
            },
        }


# -------------------------
# RESET MEMORY (NEW)
# -------------------------
@app.post("/reset")
def reset_memory():
    memory.clear()
    return {"message": "Memory cleared"}
