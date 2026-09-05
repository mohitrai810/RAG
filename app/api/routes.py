from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from app.api.dependencies import (
    get_embedding_provider,
    get_rag_service,
)
from fastapi import status

from app.core.database import SessionLocal
from app.models import (
    Job,
    JobStatus,
    Document,
    Chunk,
)
from app.queue.service import enqueue_ingestion_job
from app.api.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
    JobResponse,
    DocumentResponse
)
from app.rag.service import RAGService
from app.cache.query_cache import (
    build_query_cache_key,
    get_cached_answer,
    cache_answer,
    clear_query_cache
)

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
    status_code=status.HTTP_202_ACCEPTED,
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

    try:
        # 1. Create job in PostgreSQL
        with SessionLocal() as session:
            job = Job(
                tenant_id=tenant_id,
                filename=file.filename or "unknown",
                status=JobStatus.QUEUED,
            )

            session.add(job)
            session.commit()
            session.refresh(job)

            job_id = job.id

        # 2. Save uploaded file so the worker can use it later
        upload_dir = Path("data/uploads") / str(job_id)
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = upload_dir / (file.filename or f"document{suffix}")

        with open(file_path, "wb") as saved_file:
            saved_file.write(file.file.read())

        # 3. Tell Redis that this job is waiting
        enqueue_ingestion_job(job_id)

        # 4. Return immediately
        return UploadResponse(
            job_id=job_id,
            tenant_id=tenant_id,
            filename=file.filename or "unknown",
            status=JobStatus.QUEUED.value,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

@router.get("/jobs/{job_id}", response_model= JobResponse)
def get_job(job_id:UUID):
    with SessionLocal() as session:
        job = session.get(Job,job_id)

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Job not found")

        return JobResponse(
    job_id=job.id,
    tenant_id=job.tenant_id,
    filename=job.filename,
    status=job.status.value,
    document_id=job.document_id,
    error=job.error,
    created_at=job.created_at,
    started_at=job.started_at,
    completed_at=job.completed_at,
)

@router.post(
    "/query",
    response_model=QueryResponse,
)
def query_rag(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    try:
        cache_key = build_query_cache_key(
            tenant_id=request.tenant_id,
            query=request.query,
            candidate_k=request.candidate_k,
            final_k=request.final_k,
            max_distance=request.max_distance,
        )

        cached_answer = get_cached_answer(
            cache_key
        )

        if cached_answer is not None:
            return QueryResponse(
                answer=cached_answer
            )

        answer = rag_service.ask(
            query=request.query,
            tenant_id=request.tenant_id,
            candidate_k=request.candidate_k,
            final_k=request.final_k,
            max_distance=request.max_distance,
        )

        cache_answer(
            cache_key,
            answer,
        )

        return QueryResponse(
            answer=answer
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

@router.post("/query/stream")
def query_rag_stream(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    cache_key = build_query_cache_key(
        tenant_id=request.tenant_id,
        query=request.query,
        candidate_k=request.candidate_k,
        final_k=request.final_k,
        max_distance=request.max_distance,
    )

    cached_answer = get_cached_answer(
        cache_key
    )

    if cached_answer is not None:

        def cached_stream():
            yield cached_answer

        return StreamingResponse(
            cached_stream(),
            media_type="text/plain",
        )

    def generate_and_cache():
        chunks = []

        for chunk in rag_service.stream(
            query=request.query,
            tenant_id=request.tenant_id,
            candidate_k=request.candidate_k,
            final_k=request.final_k,
            max_distance=request.max_distance,
        ):
            chunks.append(chunk)

            yield chunk

        full_answer = "".join(chunks)

        cache_answer(
            cache_key,
            full_answer,
        )

    return StreamingResponse(
        generate_and_cache(),
        media_type="text/plain",
    )

@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    tenant_id: UUID,
):
    with SessionLocal() as session:
        documents = (
            session.query(Document)
            .filter(Document.tenant_id == tenant_id)
            .order_by(Document.created_at.desc())
            .all()
        )

        return [
            DocumentResponse(
                document_id=document.id,
                filename=document.source,
                created_at=document.created_at,
            )
            for document in documents
        ]

@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    tenant_id: UUID,
):
    with SessionLocal() as session:
        document = (
            session.query(Document)
            .filter(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        session.query(Chunk).filter(
            Chunk.document_id == document.id
        ).delete(
            synchronize_session=False
        )

        session.delete(document)

        session.commit()

    clear_query_cache()