# Production RAG System

A production-oriented, multi-tenant Retrieval-Augmented Generation backend built from first principles using **FastAPI, PostgreSQL + PGVector, Redis, BGE embeddings, CrossEncoder reranking, and OpenRouter**.

The project focuses on the engineering around RAG systems rather than wrapping the entire pipeline inside a high-level framework.

## Architecture

```text
                         CLIENT
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
        POST /documents           POST /query
               │                       │
               ▼                       ▼
            FastAPI                RAGService
               │                       │
       Create ingestion job        BGE Embedding
               │                       │
       Save uploaded file              ▼
               │                  PGVector Search
               ▼                       │
          Redis Queue             ~20 Candidates
               │                       │
         HTTP 202 Accepted              ▼
               │                 CrossEncoder
               ▼                       │
        Background Worker          ~5 Chunks
               │                       │
       Load → Chunk → Embed              ▼
               │                 Context Builder
               ▼                       │
     PostgreSQL + PGVector               ▼
               │                   OpenRouter
               ▼                       │
        Job COMPLETED                   ▼
                                     Answer
```

Document ingestion is **asynchronous** because loading, chunking, and embedding large documents can be expensive.

The interactive query path remains **synchronous** because the user is waiting for an answer.

---

## Key Features

### RAG Pipeline

* BGE embeddings using `BAAI/bge-base-en-v1.5`
* PostgreSQL + PGVector vector storage
* cosine-distance semantic retrieval
* CrossEncoder reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`
* configurable candidate and final top-K
* grounded LLM generation through OpenRouter

### Multi-Tenancy

Every document belongs to a tenant.

Retrieval filters by `tenant_id` **inside the PostgreSQL query before reranking**, preventing chunks belonging to another tenant from entering the downstream RAG pipeline.

Document deduplication is also tenant scoped:

```text
UNIQUE(tenant_id, content_hash)
```

### Async Document Ingestion

```text
POST /documents
      ↓
Create Job (QUEUED)
      ↓
Save document
      ↓
Redis Queue
      ↓
202 Accepted

Background Worker
      ↓
PROCESSING
      ↓
Load → Chunk → Embed
      ↓
PGVector
      ↓
COMPLETED / FAILED
```

Redis acts as the queue between the API and ingestion worker, while PostgreSQL stores persistent job state.

Job states:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
```

### Retrieval Evaluation

Retrieval quality is evaluated using:

* Hit@K
* Precision@K
* Recall@K
* MRR
* retrieval latency

This allows retrieval and reranking decisions to be based on measurable results instead of manually inspecting a few queries.

---

## Tech Stack

| Area           | Technology   |
| -------------- | ------------ |
| API            | FastAPI      |
| Database       | PostgreSQL   |
| Vector Search  | PGVector     |
| Queue          | Redis        |
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
├── core/         # PostgreSQL, Redis, configuration
├── models/       # Document, Chunk, Job
├── ingestion/    # loading, chunking, metadata, persistence
├── embeddings/   # BGE embedding provider
├── retrieval/    # tenant-scoped PGVector search
├── reranking/    # CrossEncoder reranking
├── evaluation/   # retrieval metrics and runner
├── context/      # LLM context construction
├── generation/   # OpenRouter generation
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

Returns immediately with:

```json
{
  "job_id": "...",
  "tenant_id": "...",
  "filename": "document.pdf",
  "status": "queued"
}
```

The worker processes the document asynchronously.

### `POST /query`

Executes:

```text
Query
  ↓
BGE Embedding
  ↓
Tenant-Scoped PGVector Retrieval
  ↓
CrossEncoder Reranking
  ↓
Context Builder
  ↓
LLM Generation
```

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

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 6. Start ingestion worker

In another terminal:

```bash
python -m app.worker.ingestion_worker
```

Now:

```text
Upload
  ↓
FastAPI
  ↓
Redis
  ↓
Worker
  ↓
PGVector
```

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
* [x] background worker
* [x] async `POST /documents`
* [ ] `GET /jobs/{job_id}`
* [ ] Redis query caching
* [ ] streaming LLM responses
* [ ] authentication / JWT tenant resolution
* [ ] structured logging
* [ ] Prometheus + Grafana
* [ ] Nginx
* [ ] load testing
* [ ] deployment

---

## Next

The next milestone is productionizing the query path:

```text
Job Status API
      ↓
Redis Query Cache
      ↓
Streaming Responses
      ↓
Timeouts / Retries
      ↓
Metrics + Logging
      ↓
Nginx + Load Testing
```

The goal is to evolve this from a working RAG pipeline into a **measurable, fault-aware, deployable AI backend**.
