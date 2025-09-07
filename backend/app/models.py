from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    # All raw retrieved chunks from Chroma (same shape as results["documents"])
    retrieved: List[List[str]]
    # Indices (within the first retrieved list) that were selected by the CrossEncoder
    reranked_ids: List[int]
    # NEW: full Chroma result
    retrieval: Optional[Dict[str, Any]] = None

class IngestResponse(BaseModel):
    message: str
    file_name: str
    chunks: int
