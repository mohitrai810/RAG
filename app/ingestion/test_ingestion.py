from uuid import uuid4

from app.ingestion.service import ingest


tenant_a=uuid4()
tenant_b=uuid4()

print("Tenant A:",tenant_a)
print("Tenant B:",tenant_b)

file_path="data/documents/test.md"

print("\nTenant A first upload")
ingest(file_path,tenant_a)
file_path="data/documents/mohit.md"
print("\nTenant B same file")
ingest(file_path,tenant_b)
