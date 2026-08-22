from uuid import UUID

from sqlalchemy import select

from app.core.database import SessionLocal
from app.embeddings.bge import BGEEmbeddingProvider
from app.models import Chunk, Document


class RetrievalService:

    def __init__(self, embedding_provider: BGEEmbeddingProvider):
        self.embedding_provider = embedding_provider

    def search(
        self,
        query: str,
        tenant_id: UUID,
        top_k: int = 3,
        max_distance: float = 0.4,
    ):
        query_embedding = self.embedding_provider.embed_query(query)

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

        with SessionLocal() as session:
            results = session.execute(statement).all()

        return results