import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

SERVICE = os.getenv("SERVICE_NAME", "incident-assistant-app")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
APP_VERSION = os.getenv("APP_VERSION", "local")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE,
            "environment": ENVIRONMENT,
            "app_version": APP_VERSION,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


logger = logging.getLogger("incident-assistant")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

app = FastAPI(title="Incident Assistant Demo", version=APP_VERSION)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    logger.info(
        f"request_started method={request.method} path={request.url.path}",
        extra={"request_id": request_id},
    )
    try:
        response = await call_next(request)
        logger.info(
            f"request_completed status={response.status_code}",
            extra={"request_id": request_id},
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception("request_failed", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "request_id": request_id},
        )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": SERVICE,
        "environment": ENVIRONMENT,
        "version": APP_VERSION,
    }


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/demo/success")
def demo_success(request: Request):
    logger.info("operation_completed", extra={"request_id": request.state.request_id})
    return {"result": "success"}


@app.get("/demo/error")
def demo_error(request: Request):
    request_id = request.state.request_id
    logger.error(
        "redis_connection_timeout dependency=redis timeout_ms=5000",
        extra={"request_id": request_id},
    )
    logger.error(
        "payment_processing_failed error_code=DEPENDENCY_TIMEOUT",
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=503,
        content={"error": "dependency_unavailable", "request_id": request_id},
    )
