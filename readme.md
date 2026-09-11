# Production RAG Backend

A production-oriented, multi-tenant RAG backend built with **FastAPI, PostgreSQL + PGVector, Redis, BGE embeddings, hybrid retrieval, CrossEncoder reranking, OpenRouter, Prometheus, Alembic, and Docker**.

Built from first principles with a focus on retrieval quality, asynchronous ingestion, caching, tenant isolation, reliability, and observability.

## Architecture

```text
                              Client
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
          POST /documents                 POST /query
                 │                             │
                 ▼                             ▼
              FastAPI                      Redis Cache
                 │                         │         │
                 │                       HIT        MISS
                 │                         │         │
                 ▼                         ▼         ▼
        PostgreSQL Job                  Response   Retrieval
           (QUEUED)                                  │
                 │                         ┌─────────┴─────────┐
                 ▼                         │                   │
           Redis Queue                     ▼                   ▼
                 │                   Dense Search        Lexical Search
                 ▼                   BGE + PGVector      PostgreSQL FTS
        Background Worker                  HNSW                GIN
                 │                         │                   │
        Load → Chunk → Embed               └─────────┬─────────┘
                 │                                   │
                 ▼                                   ▼
        PostgreSQL + PGVector                       RRF
                                                     │
                                               Top 20 Candidates
                                                     │
                                                     ▼
                                              CrossEncoder
                                                     │
                                                Top 5 Chunks
                                                     │
                                                     ▼
                                              Context Builder
                                                     │
                                                     ▼
                                               OpenRouter LLM
                                                │          │
                                                ▼          ▼
                                            Response    Streaming
```

Documents are processed asynchronously so ingestion does not block the latency-sensitive query path.

## Retrieval

The query pipeline combines two retrieval strategies:

- **Dense Search:** `BAAI/bge-base-en-v1.5` (768d) embeddings with PGVector cosine search and HNSW indexing
- **Lexical Search:** PostgreSQL Full-Text Search with a GIN index
- **Fusion:** Reciprocal Rank Fusion (RRF) combines both rankings
- **Reranking:** CrossEncoder reranks the top 20 candidates and selects the final 5 chunks

```text
Dense (BGE + HNSW) ─────┐
                        ├── RRF ── Top 20 ── CrossEncoder ── Top 5
Lexical (FTS + GIN) ────┘
```

The reranker uses an optimized ONNX inference backend for local CPU inference.

## Retrieval Evaluation

Retrieval is evaluated independently from generation using a **90-query evaluation suite** measuring HitRate@5, Precision@5, Recall@5, MRR, and latency.

| Pipeline | HitRate@5 | MRR 
|---|---:|---:|---:|
| Dense Retrieval | 66.67% | 0.507 
| Hybrid Retrieval | 66.67% | 0.522 
| **Hybrid + CrossEncoder** | **78.89%** | **0.700**

The final two-stage retrieval pipeline improved **HitRate@5 from 66.67% to 78.89%** and **MRR from 0.507 to 0.700** compared with dense retrieval, while explicitly measuring the latency-quality tradeoff.

## Production Features

- **Multi-tenancy** with tenant filtering inside retrieval queries
- **Async ingestion** using PostgreSQL job state + Redis-backed workers
- **Redis caching** for repeated queries
- **Streaming responses** through `/query/stream`
- **LLM reliability** with timeouts, retries, and exponential backoff
- **Observability** with Prometheus metrics, structured logs, and request IDs
- **Database migrations** using Alembic
- **Containerized infrastructure** using Docker Compose

### Async Ingestion

```text
POST /documents
       │
       ▼
PostgreSQL Job (QUEUED)
       │
       ▼
   Redis Queue ──────────► 202 Accepted
       │
       ▼
Background Worker
       │
       ▼
Load → Chunk → Embed
       │
       ▼
PostgreSQL + PGVector
       │
       ▼
COMPLETED / FAILED
```

PostgreSQL provides durable job state while Redis handles queue coordination.

## Observability

Prometheus metrics track individual stages of the RAG pipeline:

```text
Embedding → Vector Search → Lexical Search → Retrieval
          → Reranking → LLM → Total RAG Latency
```

Additional metrics cover HTTP latency and cache hits/misses. Structured logs include request IDs for request-level debugging.

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

Swagger UI: `http://localhost:8000/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database / Vector Store | PostgreSQL + PGVector |
| Embeddings | BGE |
| Retrieval | HNSW + PostgreSQL FTS + RRF |
| Reranking | CrossEncoder |
| Queue / Cache | Redis |
| Generation | OpenRouter |
| ORM / Migrations | SQLAlchemy + Alembic |
| Observability | Prometheus + structured logs |
| Infrastructure | Docker Compose |

## Run Locally

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
pip install -r requirements.txt
```

Create `.env`:

```env
OPENROUTER_API_KEY=your_api_key
```

Start the services and apply migrations:

```bash
docker compose up -d
alembic upgrade head
```

API documentation: `http://localhost:8000/docs`  
Metrics: `http://localhost:8000/metrics`

## Status

**Implemented:** Multi-tenancy · Async Ingestion · BGE Embeddings · PGVector · HNSW · PostgreSQL FTS · RRF Hybrid Retrieval · CrossEncoder Reranking · 90-Query Evaluation · Redis Caching · Streaming · LLM Retries · Prometheus · Docker