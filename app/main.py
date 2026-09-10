from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes import router
from app.core.database import Base, engine
from app.middleware.request_context import request_context_middleware
from app.models import Chunk, Document, Job
from app.api.dependencies import (
    get_embedding_provider,
    get_reranker,
)

app = FastAPI(
    title="Production RAG API",
    version="0.1.0",
)

app.middleware("http")(request_context_middleware)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    get_embedding_provider()
    get_reranker()


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


app.include_router(router)