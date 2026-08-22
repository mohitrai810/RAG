from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    tenant_id: UUID
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
    max_distance: float = Field(default=0.50, ge=0.0, le=2.0)


class QueryResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    document_id: UUID
    tenant_id: UUID
    filename: str
    status: str


class HealthResponse(BaseModel):
    status: str