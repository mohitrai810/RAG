from uuid import UUID

from app.context.builder import ContextBuilder
from app.generation.service import GenerationService
from app.reranking.provider import RerankerProvider
from app.retrieval.service import RetrievalService


class RAGService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        reranker: RerankerProvider,
        context_builder: ContextBuilder,
        generation_service: GenerationService,
    ):
        self.retrieval_service = retrieval_service
        self.reranker = reranker
        self.context_builder = context_builder
        self.generation_service = generation_service

    def ask(
        self,
        query: str,
        tenant_id: UUID,
        candidate_k: int = 20,
        final_k: int = 5,
        max_distance: float = 0.50,
    ) -> str:

        candidates = self.retrieval_service.search(
            query=query,
            tenant_id=tenant_id,
            top_k=candidate_k,
            max_distance=max_distance,
        )

        results = self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=final_k,
        )

        context = self.context_builder.build(results)

        return self.generation_service.generate(
            query=query,
            context=context,
        )