from app.context.builder import ContextBuilder
from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.retrieval.service import RetrievalService


if __name__ == "__main__":
    settings = get_settings()

    provider = BGEEmbeddingProvider(settings.embedding_model)

    retrieval = RetrievalService(provider)

    results = retrieval.search(
        "what is capital of france?",
        top_k=2,
    )

    builder = ContextBuilder()

    context = builder.build(results)

    if not context:
        print("\nNo relevant context found.")
    else:
        print("\n===== CONTEXT =====\n")
        print(context)