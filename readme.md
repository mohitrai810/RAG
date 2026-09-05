# Production RAG System

A production-oriented, multi-tenant Retrieval-Augmented Generation backend built from first principles using **FastAPI, PostgreSQL + PGVector, Redis, BGE embeddings, CrossEncoder reranking, and OpenRouter**.

The project focuses on the engineering around RAG systems rather than hiding the complete pipeline behind a high-level RAG framework.

## Architecture

```text
                              CLIENT
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
       POST /documents                    POST /query
              │                           POST /query/stream
              ▼                                   │
           FastAPI                                ▼
              │                            Redis Query Cache
       Create Job (QUEUED)                  │           │
              │                            HIT         MISS
       Save uploaded file                   │           │
              │                             ▼           ▼
              ▼                          Response    RAGService
         Redis Queue                                    │
              │                                         ▼
       202 Accepted                               BGE Embedding
              │                                         │
              │                                         ▼
              │                                  PGVector Search
              │                                         │
              ▼                                  ~20 Candidates
      Background Worker                                 │
              │                                         ▼
       Job → PROCESSING                           CrossEncoder
              │                                         │
       Load → Chunk → Embed                         ~5 Chunks
              │                                         │
              ▼                                         ▼
     PostgreSQL + PGVector                       Context Builder
              │                                         │
       Job → COMPLETED                                  ▼
                                                OpenRouter LLM
                                                       │
                                    ┌──────────────────┴───────────────┐
                                    │                                  │
                                    ▼                                  ▼
                              Normal Response                    Streaming Response
                                    │                                  │
                                    └──────────────┬───────────────────┘
                                                   ▼
                                             Redis Cache
```

Document ingestion is **asynchronous** because loading, chunking, embedding, and storing large documents can be expensive.

The interactive query path remains request-driven because the user is waiting for an answer. Streaming is supported to improve perceived latency by returning generated text incrementally.

---

## Key Features

### RAG Pipeline

* BGE embeddings using `BAAI/bge-base-en-v1.5`
* PostgreSQL + PGVector vector storage
* cosine-distance semantic retrieval
* CrossEncoder reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`
* configurable candidate and final top-K
* configurable retrieval distance threshold
* grounded LLM generation through OpenRouter
* standard and streaming query endpoints

### Multi-Tenancy

Every document belongs to a tenant.

Retrieval filters by `tenant_id` **inside the PostgreSQL query before reranking**, preventing chunks belonging to another tenant from entering the downstream RAG pipeline.

Document deduplication is tenant scoped:

```text
UNIQUE(tenant_id, content_hash)
```

The query cache key also includes tenant identity and retrieval configuration so cached answers cannot accidentally cross tenant boundaries.

### Async Document Ingestion

```text
POST /documents
      ↓
Create Job (QUEUED)
      ↓
Save uploaded document
      ↓
Push Job ID to Redis
      ↓
202 Accepted
```

The API does not perform expensive ingestion work directly.

A separate worker process consumes the queue:

```text
Redis Queue
      ↓
Background Worker
      ↓
PROCESSING
      ↓
Load
      ↓
Chunk
      ↓
Embed
      ↓
Store in PostgreSQL + PGVector
      ↓
COMPLETED / FAILED
```

Redis acts as the queue between the API and ingestion worker, while PostgreSQL stores persistent job state.

Supported job states:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
```

Job progress can be queried using:

```text
GET /jobs/{job_id}
```

### Redis Query Cache

The query path uses Redis to avoid repeating expensive retrieval, reranking, and LLM generation for identical requests.

```text
POST /query
      ↓
Build Cache Key
      ↓
Redis GET
   ┌──┴──┐
  HIT   MISS
   │      │
   ▼      ▼
Return   Retrieval
Cache       ↓
         Reranking
            ↓
         Generation
            ↓
         Redis SETEX
            ↓
          Response
```

The cache key includes:

```text
tenant_id
normalized query
candidate_k
final_k
max_distance
```

Cached entries use a TTL so stale results eventually expire.

### Streaming LLM Responses

The backend also exposes:

```text
POST /query/stream
```

OpenRouter is called using streaming mode and generated chunks are forwarded to the client as they arrive.

```text
OpenRouter
    ↓
chunk
    ├──→ yield to client
    │
    └──→ append in memory
              ↓
       generation finishes
              ↓
        join full answer
              ↓
         cache in Redis
```

This improves **time-to-first-token** even when total LLM generation time remains similar.

### LLM Reliability

The OpenRouter generation layer includes bounded reliability handling for transient failures.

Handled cases include:

* connection timeout
* read timeout
* connection errors
* HTTP `429`
* HTTP `5xx`
* bounded retries
* exponential backoff
* cleaner failure messages

Non-transient errors such as invalid authentication are not repeatedly retried.

### Latency Instrumentation

The query pipeline measures latency for major stages:

```text
retrieval
reranking
LLM generation
total request pipeline
```

Example measurement during local testing:

```text
retrieval ≈ 1001 ms
reranking ≈ 510 ms
LLM       ≈ 5903 ms
total     ≈ 7415 ms
```

This showed that LLM generation accounted for most end-to-end latency, motivating query caching and streaming instead of prematurely optimizing retrieval.

### Document Lifecycle

Documents can be listed and deleted.

```text
GET /documents?tenant_id=...
DELETE /documents/{document_id}?tenant_id=...
```

Deleting a document removes:

```text
Document row
      ↓
Associated Chunk rows
      ↓
Stored PGVector embeddings
      ↓
Stale query cache entries
```

Embeddings are stored on chunk rows, so removing the chunks also removes their vectors from PostgreSQL.

---

## Retrieval Evaluation

Retrieval quality is evaluated using:

* Hit@K
* Precision@K
* Recall@K
* MRR
* retrieval latency

This allows retrieval and reranking decisions to be based on measurable results rather than manually inspecting a small number of queries.

---

## Tech Stack

| Area           | Technology   |
| -------------- | ------------ |
| API            | FastAPI      |
| Database       | PostgreSQL   |
| Vector Search  | PGVector     |
| Queue          | Redis        |
| Query Cache    | Redis        |
| ORM            | SQLAlchemy   |
| Embeddings     | BGE          |
| Reranking      | CrossEncoder |
| Generation     | OpenRouter   |
| Infrastructure | Docker       |

---

## Project Structure

```text
app/
├── api/          # FastAPI routes and schemas
├── cache/        # Redis query caching
├── core/         # PostgreSQL, Redis, configuration
├── models/       # Document, Chunk, Job
├── ingestion/    # loading, chunking, metadata, persistence
├── embeddings/   # BGE embedding provider
├── retrieval/    # tenant-scoped PGVector search
├── reranking/    # CrossEncoder reranking
├── evaluation/   # retrieval metrics and runner
├── context/      # LLM context construction
├── generation/   # OpenRouter generation + streaming
├── rag/          # RAG orchestration
├── queue/        # Redis ingestion queue
└── worker/       # background ingestion worker
```

---

## API

### `GET /health`

Basic API health check.

### `POST /documents`

Uploads a PDF, TXT, or Markdown document.

Returns immediately:

```json
{
  "job_id": "...",
  "tenant_id": "...",
  "filename": "document.pdf",
  "status": "queued"
}
```

The document is processed asynchronously by the ingestion worker.

### `GET /jobs/{job_id}`

Returns persistent ingestion-job state.

Example:

```json
{
  "job_id": "...",
  "tenant_id": "...",
  "filename": "document.pdf",
  "status": "completed",
  "document_id": "...",
  "error": null,
  "created_at": "...",
  "started_at": "...",
  "completed_at": "..."
}
```

### `GET /documents`

Lists documents belonging to a tenant.

```text
GET /documents?tenant_id=<tenant_uuid>
```

### `DELETE /documents/{document_id}`

Deletes a tenant-owned document and its associated chunks and embeddings.

```text
DELETE /documents/{document_id}?tenant_id=<tenant_uuid>
```

Related query cache entries are invalidated to avoid returning answers generated from deleted content.

### `POST /query`

Executes the synchronous cached RAG path:

```text
Query
  ↓
Redis Cache
  ↓ MISS
BGE Embedding
  ↓
Tenant-Scoped PGVector Retrieval
  ↓
CrossEncoder Reranking
  ↓
Context Builder
  ↓
LLM Generation
  ↓
Cache Answer
  ↓
Response
```

### `POST /query/stream`

Runs the same RAG pipeline while streaming generated text back to the client.

The complete generated answer is accumulated during streaming and cached after generation finishes.

---

## Running Locally

### 1. Clone

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
```

### 2. Create environment

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure `.env`

```env
DATABASE_URL=postgresql+psycopg://raguser:ragpassword@localhost:5433/ragdb
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSIONS=768
OPENROUTER_API_KEY=your_api_key
```

### 4. Start infrastructure

```bash
docker compose up -d
```

This starts:

```text
PostgreSQL + PGVector
Redis
```

### 5. Start API

```bash
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### 6. Start ingestion worker

The worker is a **separate process** from the API.

In another terminal:

```bash
python -m app.worker.ingestion_worker
```

Local architecture:

```text
Terminal 1
FastAPI

Terminal 2
Ingestion Worker

Docker
├── PostgreSQL + PGVector
└── Redis
```

The worker continuously waits for ingestion jobs using Redis.

---

## Current Status

* [x] PDF / TXT / Markdown ingestion
* [x] BGE embeddings
* [x] PostgreSQL + PGVector
* [x] tenant-isolated retrieval
* [x] tenant-aware deduplication
* [x] CrossEncoder reranking
* [x] grounded LLM generation
* [x] FastAPI API
* [x] retrieval evaluation
* [x] Redis ingestion queue
* [x] persistent ingestion jobs
* [x] background ingestion worker
* [x] async `POST /documents`
* [x] `GET /jobs/{job_id}`
* [x] Redis query caching
* [x] cache TTL
* [x] query latency instrumentation
* [x] LLM timeout handling
* [x] transient failure retries
* [x] streaming LLM responses
* [x] streamed-response caching
* [x] document listing
* [x] document deletion
* [x] chunk + embedding cleanup
* [x] query cache invalidation on document deletion
* [ ] authentication / JWT tenant resolution
* [ ] structured logging
* [ ] Prometheus metrics
* [ ] Grafana dashboards
* [ ] Nginx reverse proxy
* [ ] load testing
* [ ] API + worker containerization
* [ ] deployment

---

## Next Milestone

The query and ingestion paths are now functional. The next milestone is **observability and deployment hardening**.

```text
Structured Logging
      ↓
Service Health Checks
      ↓
Prometheus Metrics
      ↓
Grafana
      ↓
Dockerize API + Worker
      ↓
Nginx
      ↓
Load Testing
      ↓
Deployment
```

The goal is to evolve the project from a working production-style RAG backend into a **measurable, fault-aware, independently scalable, deployable AI system**.
