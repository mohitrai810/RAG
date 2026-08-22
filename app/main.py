from fastapi import FastAPI

from app.api.routes import router
from app.core.database import Base, engine
from app.models import Chunk, Document


app = FastAPI(
    title="Production RAG API",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(router)