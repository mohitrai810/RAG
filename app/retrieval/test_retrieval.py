from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.retrieval.service import RetrievalService


if __name__ == "__main__":
    settings = get_settings()

    provider = BGEEmbeddingProvider(settings.embedding_model)

    retrieval = RetrievalService(provider)

    results = retrieval.search(
        "How does AOF recover data when Redis restarts?",
        top_k=2,
    )

    for chunk, distance in results:
        print("\n--- Result ---")
        print("Distance:", distance)
        print("Chunk index:", chunk.chunk_index)
        print("Content:", chunk.content)