import time
from uuid import UUID

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.metrics import RAG_COMPONENT_DURATION
from app.embeddings.bge import BGEEmbeddingProvider
from app.models import Chunk, Document


class RetrievalService:

    def __init__(self, embedding_provider: BGEEmbeddingProvider):
        self.embedding_provider = embedding_provider

    def dense_search(
        self,
        query: str,
        tenant_id: UUID,
        top_k: int,
        max_distance: float,
    ):
        embedding_start = time.perf_counter()

        query_embedding = self.embedding_provider.embed_query(query)

        RAG_COMPONENT_DURATION.labels(
            component="query_embedding"
        ).observe(time.perf_counter() - embedding_start)

        distance = Chunk.embedding.cosine_distance(query_embedding)

        statement = (
            select(Chunk, distance.label("distance"))
            .join(
                Document,
                Chunk.document_id == Document.id,
            )
            .where(
                Document.tenant_id == tenant_id,
                Chunk.embedding.is_not(None),
                distance <= max_distance,
            )
            .order_by(distance)
            .limit(top_k)
        )

        vector_start = time.perf_counter()

        with SessionLocal() as session:
            results = session.execute(statement).all()

        RAG_COMPONENT_DURATION.labels(
            component="vector_search"
        ).observe(time.perf_counter() - vector_start)

        return results

    def lexical_search(
        self,
        query: str,
        tenant_id: UUID,
        top_k: int,
    ):
        lexical_start = time.perf_counter()

        document_vector = func.to_tsvector(
            "english",
            Chunk.content,
        )

        query_vector = func.plainto_tsquery(
            "english",
            query,
        )

        lexical_score = func.ts_rank(
            document_vector,
            query_vector,
        )

        statement = (
            select(
                Chunk,
                lexical_score.label("lexical_score"),
            )
            .join(
                Document,
                Chunk.document_id == Document.id,
            )
            .where(
                Document.tenant_id == tenant_id,
                document_vector.op("@@")(query_vector),
            )
            .order_by(lexical_score.desc())
            .limit(top_k)
        )

        with SessionLocal() as session:
            results = session.execute(statement).all()

        RAG_COMPONENT_DURATION.labels(
            component="lexical_search"
        ).observe(time.perf_counter() - lexical_start)

        return results

    def search(
        self,
        query: str,
        tenant_id: UUID,
        top_k: int = 3,
        max_distance: float = 0.4,
    ):
        return self.dense_search(
            query=query,
            tenant_id=tenant_id,
            top_k=top_k,
            max_distance=max_distance,
        )