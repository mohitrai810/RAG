from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.embeddings.bge import BGEEmbeddingProvider
from app.ingestion.service import ingest


CORPUS_DIR = Path("data/technical-troubleshooting-corpus/documents")
EVALUATION_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")


def main():
    settings = get_settings()

    embedding_provider = BGEEmbeddingProvider(
        settings.embedding_model
    )

    documents = sorted(CORPUS_DIR.glob("*.md"))

    print(f"Found {len(documents)} Markdown documents")
    print(f"Evaluation tenant: {EVALUATION_TENANT_ID}")

    for document_path in documents:
        print(f"\nIngesting: {document_path.name}")

        ingest(
            file_path=str(document_path),
            tenant_id=EVALUATION_TENANT_ID,
            embedding_provider=embedding_provider,
            source_name=document_path.name,
        )


if __name__ == "__main__":
    main()