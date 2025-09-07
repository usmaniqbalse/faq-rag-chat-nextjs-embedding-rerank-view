import time
import logging
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ingest, ask

from app.logging_config import setup_logging, set_request_id
from app.exceptions import install_exception_handlers

# Configure logging before app initialization
setup_logging(level=settings.LOG_LEVEL, json_logs=settings.LOG_JSON)
logger = logging.getLogger("app")

app = FastAPI(title="RAG Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware + simple access log
@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = rid
    set_request_id(rid)

    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        # Minimal structured access log
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": getattr(locals().get("response", None), "status_code", 0),
                "duration_ms": duration_ms,
                "client": request.client.host if request.client else None,
            },
        )
        # Clear request id after request ends
        set_request_id("-")

# Routers
app.include_router(ingest.router)
app.include_router(ask.router)

# Global exception handlers
install_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
