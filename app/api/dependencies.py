from functools import lru_cache
from app.reranking.cross_encoder import CrossEncoderReranker
from app.context.builder import ContextBuilder
from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.generation.openrouter import OpenRouterProvider
from app.generation.service import GenerationService
from app.rag.service import RAGService
from app.retrieval.service import RetrievalService


@lru_cache
def get_embedding_provider() -> BGEEmbeddingProvider:
    settings = get_settings()

    return BGEEmbeddingProvider(
        settings.embedding_model
    )


@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_provider=get_embedding_provider()
    )


@lru_cache
def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


@lru_cache
def get_generation_service() -> GenerationService:
    settings = get_settings()

    provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key
    )

    return GenerationService(
        provider=provider
    )


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(
        retrieval_service=get_retrieval_service(),
        reranker=get_reranker(),
        context_builder=get_context_builder(),
        generation_service=get_generation_service(),
    )

@lru_cache
def get_reranker():
    return CrossEncoderReranker()