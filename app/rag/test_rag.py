from uuid import UUID

from app.context.builder import ContextBuilder
from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.generation.openrouter import OpenRouterProvider
from app.generation.service import GenerationService
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService
from app.reranking.cross_encoder import CrossEncoderReranker


if __name__ == "__main__":
    settings = get_settings()

    embedding_provider = BGEEmbeddingProvider(
        settings.embedding_model,
    )

    retrieval_service = RetrievalService(
        embedding_provider=embedding_provider,
    )

    reranker = CrossEncoderReranker()

    context_builder = ContextBuilder()

    generation_provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key,
    )

    generation_service = GenerationService(
        provider=generation_provider,
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        reranker=reranker,
        context_builder=context_builder,
        generation_service=generation_service,
    )

    query = input("Enter your query: ")

    tenant_id = UUID(
        input("Enter tenant id: ")
    )

    answer = rag_service.ask(
        query=query,
        tenant_id=tenant_id,
        candidate_k=20,
        final_k=5,
    )

    print("\n===== RAG ANSWER =====\n")
    print(answer)