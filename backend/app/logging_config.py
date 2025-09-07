import json
import logging
import logging.config
from contextvars import ContextVar
from typing import Any, Dict

# Request ID context (set in middleware)
_request_id: ContextVar[str] = ContextVar("request_id", default="-")

def set_request_id(value: str) -> None:
    _request_id.set(value)

class RequestIdFilter(logging.Filter):
    """Injects request_id from contextvar into each log record."""
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        record.request_id = _request_id.get("-")
        return True

class JsonFormatter(logging.Formatter):
    """Very small JSON log formatter (no extra deps)."""
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        base: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        # Add common http fields if present via `extra=...`
        for key in ("method", "path", "status_code", "duration_ms", "client"):
            if hasattr(record, key):
                base[key] = getattr(record, key)
        # Include exception info if present
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure logging for app + uvicorn.
    - level: "DEBUG" | "INFO" | "WARNING" | "ERROR"
    - json_logs: True -> structured JSON, False -> pretty text
    """
    fmt_text = (
        "%(asctime)s | %(levelname)s | %(name)s | rid=%(request_id)s | "
        "%(message)s"
    )

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "filters": ["request_id"],
            "formatter": "json" if json_logs else "text",
        }
    }

    formatters = {
        "text": {"format": fmt_text, "datefmt": "%Y-%m-%dT%H:%M:%S%z"},
        "json": {"()": JsonFormatter},
    }

    filters = {"request_id": {"()": RequestIdFilter}}

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "filters": filters,
            "handlers": handlers,
            "loggers": {
                # Your app
                "app": {"handlers": ["console"], "level": level, "propagate": False},
                # Third-party
                "uvicorn": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.access": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.error": {"handlers": ["console"], "level": level, "propagate": False},
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
