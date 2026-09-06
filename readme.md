# Production RAG Backend

A production-oriented, multi-tenant RAG backend built with **FastAPI, PostgreSQL + PGVector, Redis, BGE embeddings, CrossEncoder reranking, OpenRouter, Prometheus, and Docker**.

Built from first principles to explore the engineering behind production RAG systems: **retrieval quality, async ingestion, caching, tenant isolation, reliability, observability, and deployment.**

## Architecture

```text
                                  CLIENT
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
          POST /documents                       POST /query
                 │                            POST /query/stream
                 ▼                                     │
             FastAPI                                    ▼
                 │                               Redis Cache
          Create Job (QUEUED)                    │          │
                 │                              HIT        MISS
          Save Uploaded File                     │          │
                 │                               ▼          ▼
                 ▼                           Response   BGE Embedding
           Redis Queue                                      │
                 │                                          ▼
           202 Accepted                            PGVector Retrieval
                 │                                  (tenant scoped)
                 ▼                                          │
        Background Worker                            ~20 candidates
                 │                                          │
         Load → Chunk → Embed                               ▼
                 │                                   CrossEncoder
                 ▼                                          │
       PostgreSQL + PGVector                          ~5 best chunks
                 │                                          │
         COMPLETED / FAILED                                 ▼
                                                    Context Builder
                                                           │
                                                           ▼
                                                    OpenRouter LLM
                                                           │
                                                ┌──────────┴──────────┐
                                                ▼                     ▼
                                           Response              Streaming
                                                │                     │
                                                └──────────┬──────────┘
                                                           ▼
                                                      Redis Cache
```

## Highlights

- **Multi-tenant retrieval** — tenant filtering happens inside the PostgreSQL vector query before reranking.
- **Two-stage retrieval** — BGE + PGVector retrieves candidates, then a CrossEncoder reranks the strongest chunks.
- **Async ingestion** — uploads create persistent PostgreSQL jobs and are processed through a Redis-backed worker.
- **Query caching** — exact Redis cache keyed by tenant, normalized query, and retrieval configuration with TTL.
- **Streaming generation** — `/query/stream` forwards LLM tokens while accumulating the final answer for caching.
- **LLM reliability** — timeouts, bounded retries, exponential backoff, `429` and `5xx` handling.
- **Observability** — structured JSON logs, request-ID correlation, and Prometheus metrics.
- **Document lifecycle** — tenant-aware listing/deletion with chunk, embedding, and cache cleanup.
- **Containerized services** — FastAPI, worker, PostgreSQL + PGVector, and Redis run through Docker Compose.

## RAG Pipeline

```text
Query
  ↓
BGE Embedding
  ↓
Tenant-Scoped PGVector Search
  ↓
~20 Candidates
  ↓
CrossEncoder Reranking
  ↓
~5 Chunks
  ↓
Context Builder
  ↓
OpenRouter LLM
  ↓
Answer
```

**Embeddings:** `BAAI/bge-base-en-v1.5` (768 dimensions)  
**Reranker:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

## Async Ingestion

```text
POST /documents
      ↓
PostgreSQL Job (QUEUED)
      ↓
Redis Queue ──────────────→ 202 Accepted
      ↓
Background Worker
      ↓
PROCESSING
      ↓
Load → Chunk → Embed
      ↓
PostgreSQL + PGVector
      ↓
COMPLETED / FAILED
```

PostgreSQL stores durable job state while Redis handles queue coordination.

```http
GET /jobs/{job_id}
```

## Retrieval Evaluation

Retrieval is evaluated using a **40-query evaluation suite** rather than only manually inspecting answers.

Metrics:

- Hit@K
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Retrieval latency

This makes retrieval and reranking changes measurable.

## Observability

Every request receives an `X-Request-ID` which is propagated into structured logs.

Prometheus metrics are exposed at:

```http
GET /metrics
```

Tracked metrics include:

- HTTP request count and latency
- Redis cache hits/misses
- retrieval latency
- reranking latency
- LLM latency
- total RAG pipeline latency

Request and tenant IDs stay in logs rather than Prometheus labels to avoid high-cardinality metrics.

### Example Local Latency

```text
Retrieval      ~421 ms
Reranking      ~1.20 s
LLM            ~4.27 s
RAG Total      ~5.90 s

Exact cache hit: ~5–7 ms
```

These are local development measurements, not production load-test results.

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/documents` | Queue document ingestion |
| `GET` | `/jobs/{job_id}` | Get ingestion status |
| `GET` | `/documents` | List tenant documents |
| `DELETE` | `/documents/{id}` | Delete document |
| `POST` | `/query` | Cached RAG query |
| `POST` | `/query/stream` | Streaming RAG query |

Swagger:

```text
http://localhost:8000/docs
```

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | PostgreSQL + PGVector |
| ORM | SQLAlchemy |
| Queue / Cache | Redis |
| Embeddings | BGE |
| Reranking | CrossEncoder |
| Generation | OpenRouter |
| Observability | Prometheus + structured JSON logs |
| Infrastructure | Docker Compose |

## Run with Docker

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
```

Create `.env`:

```env
OPENROUTER_API_KEY=your_api_key
```

Build and start:

```bash
docker compose build
docker compose up -d
```

Check services:

```bash
docker compose ps
```

Open:

```text
Swagger:  http://localhost:8000/docs
Metrics:  http://localhost:8000/metrics
```

## Project Structure

```text
app/
├── api/          # FastAPI routes
├── cache/        # Redis query cache
├── core/         # DB, Redis, logging, metrics, config
├── models/       # Document, Chunk, Job
├── ingestion/    # document ingestion
├── embeddings/   # BGE embeddings
├── retrieval/    # PGVector retrieval
├── reranking/    # CrossEncoder
├── evaluation/   # retrieval evaluation
├── generation/   # OpenRouter + streaming
├── rag/          # RAG orchestration
├── queue/        # Redis ingestion queue
└── worker/       # background worker
```

## Status

**Implemented:** retrieval evaluation, multi-tenancy, reranking, async ingestion, Redis caching, streaming, LLM retries/timeouts, document lifecycle, structured logging, Prometheus metrics, and Dockerized services.
