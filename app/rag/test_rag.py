from app.context.builder import ContextBuilder
from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.generation.openrouter import OpenRouterProvider
from app.generation.service import GenerationService
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService


if __name__ == "__main__":
    settings = get_settings()

    embedding_provider = BGEEmbeddingProvider(
        settings.embedding_model,
    )

    retrieval_service = RetrievalService(
        embedding_provider=embedding_provider,
    )

    context_builder = ContextBuilder()

    generation_provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key,
    )

    generation_service = GenerationService(
        provider=generation_provider,
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        context_builder=context_builder,
        generation_service=generation_service,
    )

    answer = rag_service.ask(
        input("Enter your query : "),
        top_k=2,
    )

    print("\n===== RAG ANSWER =====\n")
    print(answer)