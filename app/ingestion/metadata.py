from uuid import uuid4
from langchain_core.documents import Document


def enrich_chunks(
    chunks: list[Document],
    document_id: str,
    source: str,
) -> list[Document]:
    enriched_chunks = []

    for index, chunk in enumerate(chunks):
        metadata = {
            **chunk.metadata,
            "document_id": document_id,
            "source": source,
            "chunk_index": index,
            "content_type": "text",
        }

        enriched_chunks.append(
            Document(
                page_content=chunk.page_content,
                metadata=metadata,
            )
        )

    return enriched_chunks


def create_document_id() -> str:
    return str(uuid4())