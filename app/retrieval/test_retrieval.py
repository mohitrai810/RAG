from uuid import UUID

from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.retrieval.service import RetrievalService


if __name__ == "__main__":
    settings = get_settings()

    provider = BGEEmbeddingProvider(settings.embedding_model)

    retrieval = RetrievalService(provider)

    tenant_id = UUID("f1786847-ef06-4306-bebc-09a5993c9f5e")

    results = retrieval.search(
        "Tell about mohit",
        tenant_id=tenant_id,
        top_k=2,
    )
    assert len(results)>0
    for chunk, distance in results:
        print("\n--- Result ---")
        print("Distance:", distance)
        print("Chunk index:", chunk.chunk_index)
        print("Content:", chunk.content)