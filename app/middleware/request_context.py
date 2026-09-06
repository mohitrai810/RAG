import time
import uuid

from fastapi import Request

from app.core.logging import log_event
from app.core.request_context import request_id_context
from app.core.metrics import HTTP_REQUESTS, HTTP_REQUEST_DURATION


async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    token = request_id_context.set(request_id)

    start = time.perf_counter()

    try:
        response = await call_next(request)

        total_ms = (time.perf_counter() - start) * 1000

        HTTP_REQUESTS.labels(
            method=request.method,
            path=request.url.path,
            status=str(response.status_code),
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            path=request.url.path,
        ).observe(total_ms / 1000)

        log_event(
            "http_request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(total_ms, 2),
        )

        response.headers["X-Request-ID"] = request_id

        return response

    finally:
        request_id_context.reset(token)