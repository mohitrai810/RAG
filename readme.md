# Production-Oriented RAG System

A modular Retrieval-Augmented Generation (RAG) backend built from first principles to understand and implement the systems behind modern AI retrieval pipelines.

The project intentionally avoids hiding the workflow behind a single high-level RAG abstraction. Ingestion, chunking, embeddings, vector retrieval, tenant isolation, reranking, context construction, generation, and API transport are implemented as separate services.

The current system supports a two-stage retrieval pipeline using **BGE + PGVector for candidate retrieval** and a **CrossEncoder for reranking**, exposed through a lightweight FastAPI layer.

---

## Why This Project Exists

Many RAG demos follow a simple pattern:

```text
Load PDF
   ↓
Vector Store
   ↓
LLM
   ↓
Answer
```

That is useful for prototyping, but production-oriented RAG systems need much more structure.

This project focuses on understanding and implementing:

- document lifecycle and persistence
- chunking and metadata
- embedding generation
- PostgreSQL + PGVector storage
- semantic vector retrieval
- tenant-aware data isolation
- document deduplication
- two-stage retrieval and reranking
- service boundaries and provider abstractions
- grounded LLM generation
- FastAPI transport
- measurable retrieval quality
- extensibility toward evaluation, citations, authentication, and observability

---

# Architecture

## Current Architecture

```text
                          ┌──────────────────┐
                          │     DOCUMENT     │
                          │   PDF / TXT / MD │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  Content Hashing │
                          └────────┬─────────┘
                                   │
                                   ▼
                      Tenant-Aware Duplicate Check
                                   │
                           ┌───────┴────────┐
                           │                │
                      Duplicate          New File
                           │                │
                        Return             ▼
                                   ┌──────────────────┐
                                   │ Document Loader  │
                                   └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │     Chunker      │
                                   │ Recursive Split  │
                                   └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │ Metadata Enrich. │
                                   └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  BGE Embeddings  │
                                   │  768 Dimensions  │
                                   └────────┬─────────┘
                                            │
                                            ▼
                          ┌────────────────────────────────┐
                          │     PostgreSQL + PGVector      │
                          │                                │
                          │ Documents                      │
                          │   └── tenant_id                │
                          │                                │
                          │ Chunks                         │
                          │   └── embedding VECTOR(768)    │
                          └──────────────┬─────────────────┘
                                         │
                                         ▼
                                      USER QUERY
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ Query Embedding  │
                                │       BGE        │
                                └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ RetrievalService │
                                └────────┬─────────┘
                                         │
                                         ▼
                              Tenant-Scoped DB Filter
                                         │
                                         ▼
                           PGVector Cosine Distance Search
                                         │
                                         ▼
                            Candidate Retrieval (~20)
                                         │
                                         ▼
                           ┌────────────────────────┐
                           │ CrossEncoder Reranker  │
                           │ ms-marco-MiniLM-L-6-v2 │
                           └───────────┬────────────┘
                                       │
                                       ▼
                                Final Top-K (~5)
                                       │
                                       ▼
                                ┌──────────────────┐
                                │ Context Builder  │
                                └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ GenerationService│
                                └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ OpenRouter       │
                                │ Generation       │
                                └────────┬─────────┘
                                         │
                                         ▼
                                       ANSWER
```

---

# Multi-Tenant Data Isolation

The RAG engine is designed so retrieval is scoped to the tenant requesting the information.

A document belongs to a tenant:

```text
Tenant
   ↓
Document
   ↓
Chunks
```

The `documents` table contains a `tenant_id`, and retrieval joins chunks back to their parent document before semantic search.

Conceptually:

```sql
SELECT chunks, distance
FROM chunks
JOIN documents
    ON chunks.document_id = documents.id
WHERE documents.tenant_id = :tenant_id
ORDER BY distance
LIMIT :candidate_k;
```

Tenant filtering happens **inside the database query before reranking**.

This is important because chunks belonging to another tenant should never be exposed to the reranker, context builder, or generation model.

---

## Tenant-Aware Deduplication

Document deduplication is scoped per tenant.

Instead of enforcing:

```text
content_hash UNIQUE
```

the database uses:

```text
UNIQUE(tenant_id, content_hash)
```

This means:

```text
Tenant A + Document X  → allowed
Tenant B + Document X  → allowed
Tenant A + Document X  → duplicate
```

The document hash is checked before chunking and embedding, avoiding unnecessary embedding computation for documents already ingested by the same tenant.

---

# How It Works

## 1. Document Ingestion

```text
Document
   ↓
SHA-256 Hash
   ↓
Tenant-Aware Duplicate Check
   ↓
Loader
   ↓
Recursive Chunker
   ↓
Metadata Enrichment
   ↓
BGE Embeddings
   ↓
PostgreSQL + PGVector
```

Supported formats:

- PDF
- TXT
- Markdown

Documents are split into smaller overlapping chunks so retrieval operates on focused semantic units instead of embedding an entire document as one vector.

Each chunk receives metadata such as:

```text
document_id
source
chunk_index
content_type
```

Chunk text is embedded using:

```text
BAAI/bge-base-en-v1.5
```

with 768-dimensional embeddings.

---

## 2. Candidate Retrieval

When a tenant submits a query:

```text
Query
   ↓
BGE Query Embedding
   ↓
768-Dimensional Vector
   ↓
Tenant Filter
   ↓
PGVector Cosine Distance Search
   ↓
Candidate Top-K
   ↓
Distance Threshold
```

The same BGE model is used for documents and queries so both exist in the same embedding space.

Candidate retrieval supports:

- cosine-distance search
- configurable candidate count
- configurable distance threshold
- tenant-scoped filtering

Vector retrieval is optimized for fast broad candidate selection.

---

## 3. CrossEncoder Reranking

Vector similarity is fast, but query and chunk embeddings are produced independently.

The reranking stage processes the **query and candidate chunk together** using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

For each candidate:

```text
(query, chunk)
      ↓
CrossEncoder
      ↓
relevance score
```

Candidates are sorted by their CrossEncoder relevance score, and only the highest-ranked chunks are passed to the context builder.

Current retrieval strategy:

```text
PGVector candidate retrieval
        ↓
~20 candidates
        ↓
CrossEncoder reranking
        ↓
~5 final chunks
```

This keeps vector search responsible for scalable candidate generation while using the more expensive CrossEncoder only on a small candidate set.

---

## 4. Context Construction

Reranked chunks are formatted into structured context containing information such as:

```text
SOURCE
CHUNK INDEX
DISTANCE
CONTENT
```

The context layer remains independent of the retrieval and generation implementations.

---

## 5. Generation

```text
User Question
      +
Reranked Context
      ↓
GenerationService
      ↓
GenerationProvider
      ↓
OpenRouter
      ↓
Answer
```

The generation layer is separated from the provider implementation, making it possible to support additional providers later without rewriting the RAG orchestration layer.

If retrieval returns no suitable context, the system avoids blindly asking the LLM to generate an answer from unrelated outside knowledge.

---

# FastAPI Layer

The core RAG engine is exposed through FastAPI.

Current endpoints:

```text
GET  /health
POST /documents
POST /query
```

### `GET /health`

Basic service health endpoint.

### `POST /documents`

Accepts:

- `tenant_id`
- PDF, TXT, or Markdown file

The uploaded file is passed into the existing ingestion pipeline.

### `POST /query`

Accepts a query and tenant identifier, then executes:

```text
tenant-scoped retrieval
        ↓
CrossEncoder reranking
        ↓
context construction
        ↓
generation
```

Tenant identity is currently supplied explicitly by the caller. Authentication-derived tenant identity is a future improvement.

---

# Project Structure

```text
RAG/
│
├── app/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── health.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   └── chunk.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── metadata.py
│   │   ├── service.py
│   │   └── test_ingestion.py
│   │
│   ├── embeddings/
│   │   ├── provider.py
│   │   ├── bge.py
│   │   └── test_embedding.py
│   │
│   ├── retrieval/
│   │   ├── service.py
│   │   └── test_retrieval.py
│   │
│   ├── reranking/
│   │   ├── __init__.py
│   │   ├── provider.py
│   │   ├── cross_encoder.py
│   │   └── test_flashrank.py
│   │
│   ├── context/
│   │   ├── builder.py
│   │   └── test_context.py
│   │
│   ├── generation/
│   │   ├── provider.py
│   │   ├── openrouter.py
│   │   ├── service.py
│   │   └── test_generation.py
│   │
│   ├── rag/
│   │   ├── service.py
│   │   └── test_rag.py
│   │
│   └── main.py
│
├── data/
│   └── documents/
│
├── docker-compose.yaml
├── requirements.txt
├── .gitignore
└── readme.md
```

> Note: the reranking test file can be renamed to `test_reranking.py` later if the old FlashRank-specific filename is still present.

---

# Core Components

| Component | Responsibility |
| --- | --- |
| `ingestion` | Document loading, deduplication, chunking, metadata, and persistence |
| `embeddings` | Document and query embedding generation |
| `models` | SQLAlchemy database models |
| `retrieval` | Tenant-scoped PGVector candidate retrieval |
| `reranking` | CrossEncoder relevance reranking |
| `context` | Converts reranked chunks into LLM context |
| `generation` | Provider-independent LLM generation |
| `rag` | Orchestrates retrieval → reranking → context → generation |
| `core` | Configuration, database connections, and infrastructure utilities |
| `api` | FastAPI transport and dependency wiring |

---

# Tech Stack

## AI / Retrieval

- `BAAI/bge-base-en-v1.5`
- Sentence Transformers
- `cross-encoder/ms-marco-MiniLM-L-6-v2`
- PGVector
- OpenRouter

## Backend

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Docker

## Planned

- retrieval evaluation
- end-to-end RAG evaluation
- structured citations
- authentication
- database migrations
- automated PGVector initialization
- logging and observability

---

# Database Model

## Documents

```text
documents
--------------------------------
id
tenant_id
source
content_hash
mime_type
metadata
created_at
updated_at
```

A composite unique constraint protects against duplicate uploads within the same tenant:

```text
UNIQUE(tenant_id, content_hash)
```

## Chunks

```text
chunks
--------------------------------
id
document_id
chunk_index
content
content_hash
embedding VECTOR(768)
metadata
created_at
```

Tenant ownership is derived through the parent document:

```text
chunks.document_id
        ↓
documents.id
        ↓
documents.tenant_id
```

---

# Setup

## 1. Clone

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
```

## 2. Create Python 3.11 Virtual Environment

### Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Verify:

```bash
python --version
```

## 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## 4. Configure Environment

Create a `.env` file containing your database and model configuration.

Example:

```env
DATABASE_URL=postgresql+psycopg://raguser:ragpassword@localhost:5433/ragdb
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSIONS=768
OPENROUTER_API_KEY=your_api_key
```

Do not commit `.env` or API keys.

---

# Running Infrastructure

Start PostgreSQL + PGVector:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

For a fresh PostgreSQL volume, ensure the vector extension exists:

```bash
docker exec -it rag-postgres psql -U raguser -d ragdb
```

Then:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Automating this initialization is still planned.

---

# Running the API

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# Testing the Core Pipeline

## Test Embeddings

```bash
python -m app.embeddings.test_embedding
```

Expected embedding size:

```text
768
```

## Test Tenant-Aware Ingestion

```bash
python -m app.ingestion.test_ingestion
```

## Test Tenant-Isolated Retrieval

```bash
python -m app.retrieval.test_retrieval
```

## Test Reranking

Run the reranking-specific test used in the repository.

The important behavior to verify is:

```text
PGVector ordering
        ↓
CrossEncoder scoring
        ↓
reordered candidates
```

## Run the Complete RAG Pipeline

```bash
python -m app.rag.test_rag
```

Current execution flow:

```text
Query
   ↓
BGE Query Embedding
   ↓
Tenant-Scoped PGVector Search
   ↓
Candidate Top-K
   ↓
Distance Filtering
   ↓
CrossEncoder Reranking
   ↓
Final Top-K
   ↓
Context Builder
   ↓
Generation Service
   ↓
LLM
   ↓
Answer
```

---

# Current Status

## Core RAG Engine

- [x] PDF / TXT / Markdown ingestion
- [x] Recursive text chunking
- [x] Chunk metadata
- [x] SHA-256 document hashing
- [x] Tenant-scoped document deduplication
- [x] BGE document embeddings
- [x] BGE query embeddings
- [x] PostgreSQL persistence
- [x] PGVector storage
- [x] Semantic vector retrieval
- [x] Tenant-isolated retrieval
- [x] Distance-threshold filtering
- [x] Candidate retrieval
- [x] CrossEncoder reranking
- [x] Context construction
- [x] Generation provider abstraction
- [x] OpenRouter generation
- [x] End-to-end RAG orchestration
- [x] FastAPI health endpoint
- [x] FastAPI document upload endpoint
- [x] FastAPI query endpoint
- [x] Request/response schemas
- [x] Shared service dependency wiring

---

# Next Milestone: RAG Evaluation

The next priority is **not adding more infrastructure**.

The next goal is to measure whether the retrieval pipeline actually improves when reranking is enabled.

## Retrieval Evaluation

Create a small evaluation dataset containing:

```text
query
expected_document
expected_chunk
```

Then compare:

```text
Vector Retrieval
        vs
Vector Retrieval + CrossEncoder Reranking
```

Initial metrics:

```text
HitRate@K
MRR
Recall@K
Precision@K
```

The objective is to answer questions such as:

- Does reranking move the correct chunk higher?
- How often is the relevant chunk present in the candidate set?
- How much does MRR improve after reranking?
- What candidate count gives the best quality/latency tradeoff?

Example target reporting:

```text
PGVector MRR                  = X
PGVector + CrossEncoder MRR   = Y
```

---

# Future RAG Evaluation

After retrieval evaluation is stable, the next stage is end-to-end RAG evaluation.

Planned areas include:

```text
Faithfulness / Groundedness
Answer Relevance
Context Relevance
Citation Correctness
```

This will help identify whether failures come from:

```text
retrieval
reranking
context selection
generation
```

rather than treating RAG quality as a single opaque score.

---

# Future Improvements

- structured source attribution
- authentication and auth-derived tenant identity
- automated evaluation pipeline
- proper automated test suite
- database migrations
- automated PGVector initialization
- API error handling improvements
- asynchronous provider calls
- logging and observability
- optional alternative reranking providers

---

# Goal

The long-term goal is to build a production-oriented multi-tenant knowledge platform where users can securely upload documents and query only their own knowledge base through a reliable and measurable RAG backend.

The project is developed incrementally with emphasis on understanding the engineering decisions behind retrieval, reranking, evaluation, and generation rather than assembling a black-box demo.
