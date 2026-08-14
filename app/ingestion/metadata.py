from uuid import uuid4
from langchain_core.documents import Document
from hashlib import sha256

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

def hash_text(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def hash_file(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return sha256(file.read()).hexdigest()