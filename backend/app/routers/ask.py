from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder  # helps with non-JSON-native types
from ..deps import verify_api_key
from ..models import AskRequest, AskResponse
from ..services.vector_store import query_collection
from ..services.rerank import rerank_top3
from ..services.llm import answer_from_context

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["ask"])

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, _: bool = Depends(verify_api_key)):
    # 1) Retrieve from Chroma
    results = query_collection(req.question) or {}
    # results["documents"] has shape: List[List[str]]
    documents = results.get("documents", [[]])

    # Handle no hits
    if not documents or not documents[0]:
        return AskResponse(
            answer="No relevant context found. Please ingest a PDF first.",
            retrieved=documents,
            reranked_ids=[],
            retrieval=jsonable_encoder(results),  # still return the empty/partial payload
        )
    
    # 2) Re-rank the top set for better relevance (top-3 concatenated)
    #    Pass the *first* list (the candidates for this single query)
    context, ids = rerank_top3(req.question, documents[0])

    # 3) Generate grounded answer
    answer = answer_from_context(context=context, question=req.question)

    logger.debug("Ask completed", extra={"path": "/v1/ask", "method": "POST"})
    
    # 4) Return everything the UI needs:
    #    - answer (final message)
    #    - retrieved (raw retrieved documents)
    #    - reranked_ids (indices within retrieved[0] that were selected)
    return AskResponse(
        answer=answer,
        retrieved=documents,
        reranked_ids=ids,
        retrieval=jsonable_encoder(results),  # ← include full raw Chroma result
    )


# 