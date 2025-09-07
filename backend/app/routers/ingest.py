from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from ..deps import verify_api_key
from ..config import settings
from ..models import IngestResponse
from ..services.document_processing import process_document
from ..services.vector_store import add_to_vector_collection

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["ingest"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...), _: bool = Depends(verify_api_key)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")
    size = 0
    # We need to read to measure size; UploadFile.file is a SpooledTemporaryFile
    pos = file.file.tell()
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(pos)
    if size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit")

    splits = process_document(file)
    normalized = file.filename.translate(str.maketrans({"-": "_", ".": "_", " ": "_"}))
    count = add_to_vector_collection(splits, normalized)

    logger.info("Ingested file", extra={"path": "/v1/ingest", "method": "POST"})

    return IngestResponse(message="Ingested successfully", file_name=file.filename, chunks=count)
