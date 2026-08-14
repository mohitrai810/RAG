from pathlib import Path
from uuid import UUID
from mimetypes import guess_type

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.embeddings.bge import BGEEmbeddingProvider
from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import load_document
from app.ingestion.metadata import (
    create_document_id,
    enrich_chunks,
    hash_file,
    hash_text,
)
from app.models import Chunk, Document


def ingest(file_path: str):
    path = Path(file_path)

    documents = load_document(file_path)

    chunker = DocumentChunker()
    chunks = chunker.split(documents)

    document_id = create_document_id()

    chunks = enrich_chunks(
        chunks,
        document_id=document_id,
        source=path.name,
    )

    settings = get_settings()
    embedding_provider = BGEEmbeddingProvider(settings.embedding_model)

    embeddings = embedding_provider.embed_documents(
        [chunk.page_content for chunk in chunks]
    )

    document_hash = hash_file(file_path)
    mime_type, _ = guess_type(path.name)

    with SessionLocal() as session:
        existing_document = session.scalar(
            select(Document).where(
                Document.content_hash == document_hash
            )
        )

        if existing_document:
            print(f"Document already exists: {existing_document.id}")
            return existing_document.id

        document = Document(
            id=UUID(document_id),
            source=path.name,
            content_hash=document_hash,
            mime_type=mime_type,
            document_metadata={
                "source": path.name,
            },
        )

        session.add(document)

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            database_chunk = Chunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk.page_content,
                content_hash=hash_text(chunk.page_content),
                embedding=embedding,
                chunk_metadata=chunk.metadata,
            )

            session.add(database_chunk)

        session.commit()

    print(f"Loaded documents: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Generated embeddings: {len(embeddings)}")
    print(f"Embedding dimensions: {embedding_provider.dimensions}")
    print(f"Stored document: {document_id}")

    return UUID(document_id)