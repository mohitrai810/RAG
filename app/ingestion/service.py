from pathlib import Path

from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import load_document
from app.ingestion.metadata import create_document_id, enrich_chunks


def ingest(file_path: str):
    documents = load_document(file_path)

    chunker = DocumentChunker()
    chunks = chunker.split(documents)

    document_id = create_document_id()

    chunks = enrich_chunks(
        chunks,
        document_id=document_id,
        source=Path(file_path).name,
    )

    print(f"Loaded documents: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Document ID: {document_id}")

    for index, chunk in enumerate(chunks):
        print(f"\n--- Chunk {index} ---")
        print("Metadata:", chunk.metadata)
        print("Content:", chunk.page_content)