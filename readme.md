# Production RAG System

A production-oriented **Retrieval-Augmented Generation (RAG)** system built from scratch to understand how modern RAG systems work internally.

The project focuses on building the core pipeline without hiding the important components behind a single framework:

* Document ingestion
* Text chunking
* Metadata
* Embeddings
* PostgreSQL + PGVector
* Semantic retrieval
* Similarity filtering
* Context construction
* LLM generation
* Provider abstraction
* RAG orchestration

The current milestone is a **complete end-to-end RAG engine**. The next stage is exposing it through a FastAPI backend and adding production features such as authentication, multi-tenancy, background processing, observability, and evaluation.

---

## Architecture

### Complete RAG Architecture

```text
                         ┌──────────────────┐
                         │     DOCUMENT     │
                         │   PDF / TXT / MD │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Document Loader │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Chunker     │
                         │ Recursive Split  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Metadata     │
                         │    Enrichment    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  BGE Embedding   │
                         │ 768 dimensions   │
                         └────────┬─────────┘
                                  │
                                  ▼
              ┌────────────────────────────────────┐
              │        PostgreSQL + PGVector       │
              │                                    │
              │  Documents                          │
              │  Chunks                             │
              │  Embeddings                         │
              └────────────────┬───────────────────┘
                               │
                               │
                         USER QUERY
                               │
                               ▼
                      ┌──────────────────┐
                      │ Query Embedding  │
                      │      BGE         │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ Retrieval Service│
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Top-K Search    │
                      │ + Distance Filter│
                      └────────┬─────────┘
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
                      │      ↓           │
                      │     Gemma        │
                      └────────┬─────────┘
                               │
                               ▼
                           ANSWER
```

---

## How It Works

### 1. Document Ingestion

A document enters the system:

```text
PDF / TXT / Markdown
        ↓
     Loader
        ↓
     Chunker
        ↓
    Metadata
        ↓
   Embeddings
        ↓
 PostgreSQL + PGVector
```

The document is split into smaller chunks because embeddings and retrieval work better with focused pieces of text.

Each chunk receives metadata and a **768-dimensional BGE embedding**.

---

### 2. Semantic Retrieval

When a user asks a question:

```text
User Query
    ↓
BGE Embedding
    ↓
Query Vector
    ↓
PGVector Similarity Search
    ↓
Top-K Chunks
    ↓
Distance Threshold
    ↓
Relevant Chunks
```

The same embedding model is used for both documents and queries so they exist in the same vector space.

The distance threshold prevents unrelated chunks from being passed to the LLM.

---

### 3. Context Construction

The retrieved chunks are formatted into a single context:

```text
Retrieved Chunks
       ↓
Context Builder
       ↓
LLM Context
```

---

### 4. Generation

The final stage is:

```text
Question + Retrieved Context
             ↓
      Generation Service
             ↓
     Generation Provider
             ↓
        OpenRouter
             ↓
           Gemma
             ↓
          Answer
```

If no relevant chunks are found, the system avoids blindly asking the LLM to answer.

---

# Project Structure

```text
RAG/
│
├── app/
│   │
│   ├── api/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   └── chunk.py
│   │
│   ├── ingestion/
│   │   ├── loaders/
│   │   ├── chunker.py
│   │   ├── metadata.py
│   │   └── test_ingestion.py
│   │
│   ├── embeddings/
│   │   ├── base.py
│   │   ├── bge.py
│   │   └── test_embedding.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   └── test_retrieval.py
│   │
│   ├── context/
│   │   ├── builder.py
│   │   └── test_context.py
│   │
│   ├── generation/
│   │   ├── base.py
│   │   ├── openrouter.py
│   │   ├── service.py
│   │   └── test_generation.py
│   │
│   ├── rag/
│   │   ├── service.py
│   │   └── test_rag.py
│   │
│   └── create_tables.py
│
├── data/
│   └── documents/
│       └── test.md
│
├── docker-compose.yml
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# Core Components

| Component    | Responsibility                        |
| ------------ | ------------------------------------- |
| `ingestion`  | Load and chunk documents              |
| `embeddings` | Generate document/query embeddings    |
| `models`     | Database models                       |
| `retrieval`  | Semantic vector search                |
| `context`    | Build LLM context                     |
| `generation` | Generate answers using LLM            |
| `rag`        | Orchestrate the complete pipeline     |
| `core`       | Configuration and database connection |
| `api`        | Future FastAPI layer                  |

---

# Tech Stack

* **Python**
* **PostgreSQL**
* **PGVector**
* **SQLAlchemy**
* **BGE `BAAI/bge-base-en-v1.5`**
* **OpenRouter**
* **Gemma**
* **Docker**
* **FastAPI** *(next stage)*

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd RAG
```

## 2. Create virtual environment

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

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment

Create `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/rag

EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIMENSION=768

OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=your_model
```

---

# Usage

## Start PostgreSQL + PGVector

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

The database is available at:

```text
localhost:5433
```

---

## Create Database Tables

```bash
python -m app.create_tables
```

Expected:

```text
Database tables created successfully.
```

---

## Test Embeddings

```bash
python -m app.embeddings.test_embedding
```

Expected:

```text
Dimension : 768
Model Dimension : 768
```

The first execution downloads the BGE model.

---

## Ingest a Document

A sample document is available at:

```text
data/documents/test.md
```

Run:

```bash
python -m app.ingestion.test_ingestion
```

Pipeline:

```text
Load
 ↓
Chunk
 ↓
Metadata
 ↓
Embedding
 ↓
Store
```

---

## Test Retrieval

```bash
python -m app.retrieval.test_retrieval
```

This performs semantic search against the stored embeddings.

Example:

```text
--- Result ---

Distance: 0.2317
Chunk index: 1

Content:
When Redis restarts, it can reconstruct the dataset
by replaying these operations.
```

---

## Test Context Builder

```bash
python -m app.context.test_context
```

This converts retrieved chunks into the context supplied to the LLM.

---

## Test Generation

```bash
python -m app.generation.test_generation
```

Flow:

```text
GenerationService
       ↓
GenerationProvider
       ↓
OpenRouterProvider
       ↓
LLM
```

---

## Run Complete RAG Pipeline

```bash
python -m app.rag.test_rag
```

This runs the complete system:

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K + Distance Filtering
 ↓
Context
 ↓
LLM
 ↓
Answer
```

---

# Current Status

### Core RAG Engine — Complete

* [x] PDF / TXT / Markdown ingestion
* [x] Recursive chunking
* [x] Metadata
* [x] BGE embeddings
* [x] PostgreSQL
* [x] PGVector
* [x] Semantic retrieval
* [x] Top-K search
* [x] Distance filtering
* [x] Context construction
* [x] LLM generation
* [x] Provider abstraction
* [x] End-to-end RAG pipeline

# Goal

The long-term goal is to evolve this core engine into a **production-grade personal knowledge platform** where users can upload documents and interact with their own knowledge base through a reliable, scalable RAG backend.
