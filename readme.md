# Production RAG Backend

A production-oriented, multi-tenant RAG backend built with **FastAPI, PostgreSQL + PGVector, Redis, BGE embeddings, CrossEncoder reranking, OpenRouter, Prometheus, Alembic, and Docker**.

Built from first principles to explore retrieval quality, async ingestion, caching, tenant isolation, observability, and production RAG architecture.

## Architecture

```text
                         Client
                           │
              ┌────────────┴────────────┐
              │                         │
       POST /documents             POST /query
              │                         │
              ▼                         ▼
           FastAPI                 Redis Cache
              │                    │        │
              ▼                   HIT      MISS
      PostgreSQL Job               │        │
              │                    ▼        ▼
         Redis Queue            Response  Retrieval
              │                             │
              ▼                    ┌────────┴────────┐
      Background Worker            ▼                 ▼
              │               BGE + PGVector    PostgreSQL FTS
       Load → Chunk → Embed       HNSW + Cosine      GIN
              │                    │                 │
              ▼                    └────────┬────────┘
      PostgreSQL + PGVector                 │
                                           ▼
                                      CrossEncoder
                                           │
                                           ▼
                                     Context Builder
                                           │
                                           ▼
                                     OpenRouter LLM
                                      │          │
                                   Response   Streaming
```

> Dense and lexical retrieval are implemented independently. RRF-based hybrid fusion is currently in progress.

## Highlights

- **Multi-tenant retrieval** with tenant filtering inside PostgreSQL queries
- **Dense retrieval** using BGE embeddings and PGVector cosine search
- **HNSW indexing** for scalable approximate nearest-neighbor search
- **Lexical retrieval** using PostgreSQL Full-Text Search with a GIN index
- **CrossEncoder reranking** over retrieved candidates
- **40-query retrieval evaluation suite** with Hit@K, Precision@K, Recall@K, MRR, and latency
- **Async ingestion** using persistent PostgreSQL jobs and a Redis-backed worker
- **Redis query caching** with tenant and retrieval configuration-aware keys
- **Streaming LLM responses** through `/query/stream`
- **Structured logging and Prometheus metrics** with per-component latency
- **Alembic migrations** for versioned database schema changes
- **Dockerized API, worker, PostgreSQL + PGVector, and Redis**

## Retrieval

```text
Dense Retrieval                    Lexical Retrieval
      │                                   │
      ▼                                   ▼
BGE Embedding                       PostgreSQL FTS
      │                                   │
      ▼                                   ▼
PGVector + HNSW                       GIN Index
      │                                   │
      └──────────────┬────────────────────┘
                     │
                RRF Fusion
                 (next)
                     │
                     ▼
                CrossEncoder
                     │
                     ▼
                 Top Chunks
                     │
                     ▼
              OpenRouter LLM
```

**Embedding model:** `BAAI/bge-base-en-v1.5` (768 dimensions)  
**Reranker:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

## Async Ingestion

```text
POST /documents
      ↓
PostgreSQL Job (QUEUED)
      ↓
Redis Queue ─────────→ 202 Accepted
      ↓
Background Worker
      ↓
Load → Chunk → Embed
      ↓
PostgreSQL + PGVector
      ↓
COMPLETED / FAILED
```

PostgreSQL stores durable job state while Redis handles queue coordination.

## Retrieval Evaluation

Retrieval changes are evaluated against a **40-query test suite** using:

- Hit@K
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Retrieval latency

This provides a measurable baseline for comparing retrieval strategies instead of relying only on generated-answer quality.

## Observability

Prometheus metrics are exposed at:

```text
GET /metrics
```

Metrics include HTTP latency, cache hits/misses, query embedding, vector search, lexical search, retrieval, reranking, LLM, and total RAG latency.

Structured logs include request IDs for request-level debugging without introducing high-cardinality Prometheus labels.

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

Swagger is available at `http://localhost:8000/docs`.

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | PostgreSQL + PGVector |
| Vector Search | HNSW + Cosine Distance |
| Lexical Search | PostgreSQL FTS + GIN |
| ORM / Migrations | SQLAlchemy + Alembic |
| Queue / Cache | Redis |
| Embeddings | BGE |
| Reranking | CrossEncoder |
| Generation | OpenRouter |
| Observability | Prometheus + structured logs |
| Infrastructure | Docker Compose |

## Run Locally

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
```

Create `.env`:

```env
OPENROUTER_API_KEY=your_api_key
```

Then:

```bash
docker compose build
docker compose up -d
alembic upgrade head
```

Open:

```text
Swagger: http://localhost:8000/docs
Metrics: http://localhost:8000/metrics
```

## Status

Implemented:

`Multi-tenancy` · `Dense Retrieval` · `HNSW` · `PostgreSQL FTS` · `CrossEncoder Reranking` · `Retrieval Evaluation` · `Async Ingestion` · `Redis Caching` · `Streaming` · `LLM Retries` · `Prometheus` · `Alembic` · `Docker`

Next: **RRF-based hybrid retrieval and evaluation against the dense-only baseline.**