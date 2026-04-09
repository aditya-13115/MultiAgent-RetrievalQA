from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str


class TraceResponse(BaseModel):
    route: str
    rewritten_query: str
    sub_queries: List[str]
    retrieved_docs: List[str]
    reasoning: str
    critic: Optional[str]


class QueryResponse(BaseModel):
    answer: str
    trace: TraceResponse
