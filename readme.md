# Production-Oriented RAG System

A modular Retrieval-Augmented Generation (RAG) backend built from first principles to understand and implement the systems behind modern AI retrieval pipelines.

The project intentionally avoids hiding the complete workflow behind a single high-level RAG abstraction. Core components such as ingestion, chunking, embeddings, vector retrieval, tenant isolation, context construction, and generation are implemented as separate services.

The goal is to evolve this repository from a working RAG engine into a production-oriented multi-tenant AI backend.

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

That is useful for prototyping, but production systems need significantly more structure.

This project focuses on understanding and implementing:

* document lifecycle and persistence
* chunking and metadata
* embedding generation
* PostgreSQL + PGVector storage
* semantic vector retrieval
* similarity filtering
* tenant-aware data isolation
* document deduplication
* service boundaries
* provider abstractions
* grounded LLM generation
* extensibility toward reranking, APIs, evaluation, and observability

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
                                        │
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
                               │ Retrieval Service│
                               └────────┬─────────┘
                                        │
                                        ▼
                         Filter by authenticated tenant
                                        │
                                        ▼
                         PGVector Cosine Distance Search
                                        │
                                        ▼
                          Top-K + Distance Threshold
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
                               │ GenerationProvider
                               │   OpenRouter     │
                               │      Gemma       │
                               └────────┬─────────┘
                                        │
                                        ▼
                                      ANSWER
```

---

# Multi-Tenant Data Isolation

The RAG engine is designed so that retrieval is scoped to the tenant requesting the information.

A document belongs to a tenant:

```text
Tenant
   ↓
Document
   ↓
Chunks
```

The `documents` table contains a `tenant_id`, and retrieval joins chunks back to their parent document before performing semantic search.

Conceptually:

```sql
SELECT chunks, distance
FROM chunks
JOIN documents
    ON chunks.document_id = documents.id
WHERE documents.tenant_id = :tenant_id
ORDER BY distance
LIMIT :top_k;
```

This ensures that one tenant's queries cannot retrieve chunks belonging to another tenant.

Tenant filtering happens inside the database query rather than after retrieval.

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

The document hash is also checked before chunking and embedding, avoiding unnecessary embedding computation for documents already ingested by the same tenant.

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

Supported formats currently include:

* PDF
* TXT
* Markdown

Documents are split into smaller overlapping chunks so that retrieval can operate on focused semantic units instead of embedding entire documents as a single vector.

Each chunk receives metadata such as:

```text
document_id
source
chunk_index
content_type
```

The chunk text is then converted into a 768-dimensional vector using:

```text
BAAI/bge-base-en-v1.5
```

---

## 2. Semantic Retrieval

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
Top-K Candidates
   ↓
Distance Threshold
   ↓
Relevant Chunks
```

The same embedding model is used for both documents and queries so that they exist in the same vector space.

Retrieval currently supports:

* cosine-distance search
* configurable `top_k`
* configurable distance threshold
* tenant-scoped retrieval

The threshold prevents clearly irrelevant chunks from being sent to the generation model.

---

## 3. Context Construction

Retrieved chunks are formatted into a structured context containing information such as:

```text
SOURCE
CHUNK INDEX
DISTANCE
CONTENT
```

This gives the generation layer both the retrieved text and information about where it came from.

---

## 4. Generation

```text
User Question
      +
Retrieved Context
      ↓
GenerationService
      ↓
GenerationProvider
      ↓
OpenRouter
      ↓
Gemma
      ↓
Answer
```

The generation layer is separated from the provider implementation.

This makes it possible to support additional backends later without rewriting the RAG orchestration layer.

Possible future providers could include:

```text
OpenAI
Anthropic
Gemini
Ollama
Local Models
```

If retrieval returns no suitable context, the system avoids blindly asking the LLM to generate an answer from outside knowledge.

---

# Project Structure

```text
RAG/
│
├── app/
│   │
│   ├── api/
│   │   └── Future FastAPI layer
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
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Core Components

| Component    | Responsibility                                                       |
| ------------ | -------------------------------------------------------------------- |
| `ingestion`  | Document loading, deduplication, chunking, metadata, and persistence |
| `embeddings` | Document and query embedding generation                              |
| `models`     | SQLAlchemy database models                                           |
| `retrieval`  | Tenant-scoped PGVector semantic retrieval                            |
| `context`    | Converts retrieved chunks into LLM context                           |
| `generation` | Provider-independent LLM generation                                  |
| `rag`        | Orchestrates retrieval → context → generation                        |
| `core`       | Configuration, database connections, and infrastructure utilities    |
| `api`        | Planned FastAPI transport layer                                      |

---

# Tech Stack

### AI / Retrieval

* BGE embeddings
* `BAAI/bge-base-en-v1.5`
* PGVector
* OpenRouter
* Gemma

### Backend

* Python
* SQLAlchemy
* PostgreSQL
* Docker

### Planned

* FastAPI
* FlashRank
* structured citations
* automated evaluation
* observability
* authentication

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

---

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

Chunks reference documents through:

```text
chunks.document_id
        ↓
documents.id
```

Tenant ownership is therefore derived through the parent document.

---

# Setup

## 1. Clone

```bash
git clone https://github.com/mohitrai810/RAG.git
cd RAG
```

---

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment

Create a `.env` file containing your database and model configuration.

Example:

```env
DATABASE_URL=postgresql+psycopg://raguser:ragpassword@localhost:5433/ragdb

EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSION=768

OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=your_model
```

Do not commit `.env` or API keys.

---

# Running the Infrastructure

Start PostgreSQL + PGVector:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

The PostgreSQL service is exposed locally through the port configured in `docker-compose.yml`.

---

## Enable PGVector

For a fresh PostgreSQL volume, the `vector` extension must exist before SQLAlchemy creates the chunk table.

Example:

```bash
docker exec -it rag-postgres psql -U raguser -d ragdb
```

Then:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This initialization will be automated in a future infrastructure improvement.

---

# Create Database Tables

```bash
python -m app.main
```

Expected:

```text
Database tables created successfully.
```

---

# Testing the Core Pipeline

## Test Embeddings

```bash
python -m app.embeddings.test_embedding
```

The BGE provider should return:

```text
Embedding dimensions: 768
```

The first run may download the embedding model.

---

## Test Tenant-Aware Ingestion

```bash
python -m app.ingestion.test_ingestion
```

The ingestion test verifies behavior such as:

```text
Tenant A uploads document
→ stored

Tenant B uploads same document
→ stored

Tenant A uploads same document again
→ duplicate detected
```

---

## Test Tenant-Isolated Retrieval

```bash
python -m app.retrieval.test_retrieval
```

Retrieval requires a tenant identifier.

Only documents owned by that tenant participate in vector search.

A document ingested under another tenant should not appear in the retrieval results.

---

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
Top-K
   ↓
Distance Filtering
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

* [x] PDF / TXT / Markdown ingestion
* [x] Recursive text chunking
* [x] Chunk metadata
* [x] SHA-256 document hashing
* [x] Tenant-scoped document deduplication
* [x] BGE document embeddings
* [x] BGE query embeddings
* [x] PostgreSQL persistence
* [x] PGVector storage
* [x] Semantic vector retrieval
* [x] Tenant-isolated retrieval
* [x] Top-K retrieval
* [x] Distance-threshold filtering
* [x] Context construction
* [x] Generation provider abstraction
* [x] OpenRouter generation
* [x] End-to-end RAG orchestration

---

# Next Milestone

The next milestone is converting the core engine into a proper AI backend service.

Planned work:

* [ ] FastAPI document upload endpoint
* [ ] FastAPI query endpoint
* [ ] health/readiness endpoints
* [ ] request/response schemas
* [ ] authentication
* [ ] tenant identity derived from authenticated requests
* [ ] structured source attribution
* [ ] FlashRank reranking
* [ ] retrieval evaluation
* [ ] proper automated tests
* [ ] database migrations
* [ ] automated PGVector initialization
* [ ] logging and observability

---

# Planned Retrieval Architecture

The next retrieval improvement will introduce a two-stage pipeline:

```text
Query
   ↓
BGE Query Embedding
   ↓
Tenant-Scoped PGVector Search
   ↓
Top ~20 Candidates
   ↓
FlashRank Reranking
   ↓
Top ~5 Chunks
   ↓
Context Builder
   ↓
LLM
```

PGVector will act as the high-recall candidate retriever, while FlashRank will provide a second relevance-ranking stage before chunks enter the LLM context.

---

# Future Evaluation

Instead of assuming reranking improves retrieval, the goal is to measure it.

Planned metrics include:

```text
HitRate@K
MRR
Precision@K
```

This will allow comparison between:

```text
Vector Retrieval
        vs
Vector Retrieval + Reranking
```

---

# Goal

The long-term goal is to build a production-oriented multi-tenant knowledge platform where users can securely upload documents and query only their own knowledge base through a reliable RAG backend.

The project is being developed incrementally with emphasis on understanding and implementing the engineering decisions behind RAG systems rather than assembling a black-box demo.
