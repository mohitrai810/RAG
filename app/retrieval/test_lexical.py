from app.core.database import SessionLocal
from app.embeddings.bge import BGEEmbeddingProvider
from app.models import Document
from app.retrieval.service import RetrievalService


with SessionLocal() as session:
    document = session.query(Document).first()

    if document is None:
        raise RuntimeError("No documents found")

    tenant_id = document.tenant_id


retrieval = RetrievalService(
    embedding_provider=BGEEmbeddingProvider("BAAI/bge-base-en-v1.5")
)

results = retrieval.lexical_search(
    query="redis",
    tenant_id=tenant_id,
    top_k=5,
)

for chunk, score in results:
    print("\n----------------")
    print("Chunk:", chunk.id)
    print("Score:", score)
    print("Content:", chunk.content[:150])