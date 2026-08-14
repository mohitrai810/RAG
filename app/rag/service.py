from app.context.builder import ContextBuilder
from app.generation.service import GenerationService
from app.retrieval.service import RetrievalService


class RAGService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilder,
        generation_service: GenerationService,
    ):
        self.retrieval_service = retrieval_service
        self.context_builder = context_builder
        self.generation_service = generation_service

    def ask(
        self,
        query: str,
        top_k: int = 3,
        max_distance: float = 0.50,
    ) -> str:

        results = self.retrieval_service.search(
            query=query,
            top_k=top_k,
            max_distance=max_distance,
        )

        context = self.context_builder.build(results)

        return self.generation_service.generate(
            query=query,
            context=context,
        )