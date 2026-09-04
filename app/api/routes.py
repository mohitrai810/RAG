from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.dependencies import get_rag_service
from fastapi import status

from app.core.database import SessionLocal
from app.models import Job, JobStatus
from app.queue.service import enqueue_ingestion_job
from app.api.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
)
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