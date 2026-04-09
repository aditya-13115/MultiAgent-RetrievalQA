import sys
import os

# 🔥 FORCE PROJECT ROOT INTO PATH (PERMANENT FIX)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from fastapi import FastAPI
from pydantic import BaseModel

from app.retrieval.retriever import BaseRetriever
from app.memory.chat_memory import ChatMemory
from app.agents.orchestrator import Orchestrator
from app.constants import INDEX_DIR

app = FastAPI()

# Init system (single instance)
retriever = BaseRetriever(INDEX_DIR)
memory = ChatMemory()
agent = Orchestrator(retriever, memory)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "Healthcare AI RAG API is running"}


@app.post("/query")
def query_api(req: QueryRequest):
    result = agent.process_query(req.query)

    # 🔥 STRUCTURED RESPONSE
    return {
        "answer": result.get("answer"),
        "trace": {
            "route": result.get("route"),
            "rewritten_query": result.get("rewritten_query"),
            "sub_queries": result.get("sub_queries"),
            "retrieved_docs": result.get("retrieved_docs"),
            "reasoning": result.get("reasoner_output"),
            "critic": result.get("critic_output"),
        }
    }