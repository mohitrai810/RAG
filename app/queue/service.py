from  uuid import UUID
from app.core.redis import redis_client

INGESTION_QUEUE = "rag:ingestion"

def enqueue_ingestion_job(job_id:UUID):
    redis_client.lpush(INGESTION_QUEUE,str(job_id))