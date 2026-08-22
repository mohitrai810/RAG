from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.dependencies import get_rag_service
from app.api.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
)
from app.ingestion.service import ingest
from app.rag.service import RAGService


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health():
    return HealthResponse(
        status="ok"
    )


@router.post(
    "/documents",
    response_model=UploadResponse,
)
def upload_document(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...),
):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and Markdown files are supported.",
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file.file.read())
            temp_path = temp_file.name

        document_id = ingest(
            temp_path,
            tenant_id,
        )

        return UploadResponse(
            document_id=document_id,
            tenant_id=tenant_id,
            filename=file.filename or "unknown",
            status="stored",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        if temp_path:
            Path(temp_path).unlink(
                missing_ok=True
            )


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_documents(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    answer = rag_service.ask(
        query=request.query,
        tenant_id=request.tenant_id,
        top_k=request.top_k,
        max_distance=request.max_distance,
    )

    return QueryResponse(
        answer=answer
    )