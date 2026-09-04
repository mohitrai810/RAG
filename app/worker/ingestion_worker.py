from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.core.database import SessionLocal
from app.core.redis import redis_client
from app.embeddings.bge import BGEEmbeddingProvider
from app.ingestion.service import ingest
from app.models import Job, JobStatus
from app.queue.service import INGESTION_QUEUE

from app.core.config import get_settings

settings = get_settings()

embedding_provider = BGEEmbeddingProvider(
    settings.embedding_model
)

def process_job(job_id: UUID):
    with SessionLocal() as session:
        job = session.get(Job, job_id)

        if not job:
            print(f"Job not found: {job_id}")
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        session.commit()

        try:
            upload_dir = Path("data/uploads") / str(job_id)

            files = list(upload_dir.iterdir())

            if not files:
                raise FileNotFoundError(
                    f"No uploaded file found for job {job_id}"
                )

            file_path = files[0]

            document_id = ingest(
                file_path=str(file_path),
                tenant_id=job.tenant_id,
                embedding_provider=embedding_provider,
                source_name=job.filename,
            )

            job.document_id = document_id
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)

            session.commit()

            print(f"Completed job: {job_id}")

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            job.completed_at = datetime.now(timezone.utc)

            session.commit()
            print(f"Failed job {job_id}: {exc}")


def run_worker():
    print("Worker started. Waiting for ingestion jobs...")
    while True:
        result = redis_client.brpop(
            INGESTION_QUEUE,
            timeout=0,
        )

        if result is None:
            continue

        _, job_id = result

        process_job(
            UUID(job_id)
        )


if __name__ == "__main__":
    run_worker()