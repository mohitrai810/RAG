# Production RAG Backend

A production-oriented, multi-tenant RAG backend built with **FastAPI, PostgreSQL + PGVector, Redis, BGE, CrossEncoder reranking, OpenRouter, Prometheus, Alembic, and Docker**.

Built from first principles with a focus on retrieval quality, async ingestion, caching, tenant isolation, reliability, and observability.

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
              │               Dense Search      Lexical Search
       Load → Chunk → Embed     BGE + PGVector    PostgreSQL FTS
              │                    HNSW              GIN
              ▼                     │                 │
      PostgreSQL + PGVector         └────────┬────────┘
                                             │
                                      CrossEncoder
                                             │
                                      Context Builder
                                             │
                                      OpenRouter LLM
                                       │          │
                                    Response   Streaming
```

> Dense and lexical retrieval are implemented independently. RRF-based hybrid fusion is the next retrieval upgrade.

## Highlights

- **Multi-tenant retrieval** with tenant filtering inside PostgreSQL queries
- **Dense retrieval** using BGE embeddings and PGVector cosine search
- **HNSW indexing** for scalable approximate nearest-neighbor vector search
- **Lexical retrieval** using PostgreSQL Full-Text Search with a GIN index
- **CrossEncoder reranking** over retrieved candidates
- **40-query evaluation suite** measuring Hit@K, Precision@K, Recall@K, MRR, and latency
- **Async ingestion** using durable PostgreSQL jobs and a Redis-backed worker
- **Redis query caching** with tenant and retrieval configuration-aware keys
- **Streaming generation** through `/query/stream`
- **LLM reliability** with timeouts, bounded retries, and exponential backoff
- **Observability** with structured logs, request IDs, and Prometheus metrics
- **Alembic migrations** for versioned schema and index changes

## Retrieval

### Dense Search

```text
Query
  ↓
BGE Embedding (768d)
  ↓
Tenant-Scoped PGVector Search
  ↓
HNSW + Cosine Distance
  ↓
Candidates
```

Dense retrieval captures semantic similarity between queries and chunks using `BAAI/bge-base-en-v1.5`.

PGVector embeddings are indexed with HNSW:

```sql
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
```

HNSW provides approximate nearest-neighbor search as the vector corpus grows. For small datasets, PostgreSQL may still choose a sequential scan when its query planner estimates it to be cheaper.

### Lexical Search

```text
Query
  ↓
PostgreSQL Full-Text Search
  ↓
GIN Index
  ↓
ts_rank
  ↓
Candidates
```

Lexical retrieval complements semantic search by matching actual terms and keywords. Chunk content is indexed using:

```sql
USING gin (to_tsvector('english', content))
```

This is useful for exact terminology, identifiers, error codes, and keywords that dense retrieval may not rank strongly.

### Reranking

Retrieved candidates are reranked using:

`cross-encoder/ms-marco-MiniLM-L-6-v2`

The highest-ranked chunks are passed to the context builder and then to the LLM.

**Next:** fuse dense and lexical rankings using Reciprocal Rank Fusion (RRF) before CrossEncoder reranking.

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

Retrieval changes are measured against a **40-query evaluation suite** using:

- Hit@K
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Retrieval latency

This provides a baseline for comparing retrieval strategies instead of relying only on generated-answer quality.

## Observability

Prometheus metrics are exposed at `GET /metrics`.

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

Swagger: `http://localhost:8000/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | PostgreSQL + PGVector |
| Vector Retrieval | BGE + HNSW |
| Lexical Retrieval | PostgreSQL FTS + GIN |
| Reranking | CrossEncoder |
| Queue / Cache | Redis |
| Generation | OpenRouter |
| ORM / Migrations | SQLAlchemy + Alembic |
| Observability | Prometheus + structured JSON logs |
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

Start the services and apply migrations:

```bash
docker compose build
docker compose up -d
alembic upgrade head
```

```text
Swagger: http://localhost:8000/docs
Metrics: http://localhost:8000/metrics
```

## Status

**Implemented:** Multi-tenancy · Dense Retrieval · HNSW · PostgreSQL FTS · CrossEncoder Reranking · Retrieval Evaluation · Async Ingestion · Redis Caching · Streaming · LLM Retries · Prometheus · Alembic · Docker

**Next:** RRF-based hybrid retrieval and evaluation against the dense-only baseline.