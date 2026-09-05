from uuid import UUID

from app.context.builder import ContextBuilder
from app.generation.service import GenerationService
from app.reranking.provider import RerankerProvider
from app.retrieval.service import RetrievalService
import time

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
        total_start = time.perf_counter()
        retrieval_start = time.perf_counter()
        candidates = self.retrieval_service.search(
        query=query,
        tenant_id=tenant_id,
        top_k=candidate_k,
        max_distance=max_distance,
        )

        retrieval_ms = (
        time.perf_counter() - retrieval_start
        ) * 1000

        rerank_start = time.perf_counter()

        results = self.reranker.rerank(
        query=query,
        results=candidates,
        top_k=final_k,
        )

        rerank_ms = (
        time.perf_counter() - rerank_start
        ) * 1000

        context = self.context_builder.build(
        results
        )

        llm_start = time.perf_counter()

        answer = self.generation_service.generate(
        query=query,
        context=context,
        )

        llm_ms = (
        time.perf_counter() - llm_start
        ) * 1000

        total_ms = (
        time.perf_counter() - total_start
        ) * 1000

        print(f"retrieval={retrieval_ms:.2f}ms | "
        f"rerank={rerank_ms:.2f}ms | "
        f"llm={llm_ms:.2f}ms | "
        f"total={total_ms:.2f}ms"
        )

        return answer
    def stream(
    self,
    query: str,
    tenant_id: UUID,
    candidate_k: int = 20,
    final_k: int = 5,
    max_distance: float = 0.50,
    ):
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
        
        yield from self.generation_service.provider.stream_generate(
        query=query,
        context=context,
        )