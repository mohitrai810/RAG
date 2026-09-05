from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
class QueryRequest(BaseModel):
    tenant_id: UUID
    query: str = Field(min_length=1)
    candidate_k: int = Field(
        default=20,
        ge=1,
        le=50,
    )

    final_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    max_distance: float = Field(
        default=0.50,
        ge=0.0,
        le=2.0,
    )


class QueryResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    job_id: UUID
    tenant_id: UUID
    filename: str
    status: str


class HealthResponse(BaseModel):
    status: str

class JobResponse(BaseModel):
    job_id: UUID
    tenant_id : UUID
    filename : str
    status : str
    document_id : UUID | None = None
    error : str | None = None
    created_at : datetime
    started_at : datetime | None = None
    completed_at : datetime | None = None
    
class DocumentResponse(BaseModel):
    document_id: UUID
    filename: str
    created_at: datetime