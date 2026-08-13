# Production RAG System

A production-oriented Retrieval-Augmented Generation (RAG) system built from scratch to understand and implement reliable document ingestion, semantic retrieval, vector search, and grounded LLM generation.

This project is intentionally built incrementally with a strong focus on **production backend engineering, retrieval quality, data modeling, observability, and understanding the systems behind RAG** rather than building a basic "chat with PDF" demo.

---

## Project Status

 **Currently under active development**

### Implemented

- [x] Dockerized PostgreSQL
- [x] PGVector extension
- [x] SQLAlchemy database layer
- [x] Document persistence model
- [x] Chunk persistence model
- [x] Document → Chunk relationship
- [x] Content hashing for document deduplication
- [x] JSON metadata storage
- [x] Configurable embedding model
- [x] Configurable embedding dimensions
- [x] Embedding provider abstraction
- [x] BGE embedding provider
- [x] Markdown document loading
- [x] Text chunking
- [x] `vector(768)` storage in PostgreSQL

### In Progress

- [ ] Download and integrate BGE embeddings
- [ ] Persist real document embeddings
- [ ] Semantic similarity retrieval
- [ ] Retrieval service
- [ ] Metadata filtering
- [ ] Query processing

### Planned

- [ ] Context construction
- [ ] Grounded LLM generation
- [ ] Source references / citations
- [ ] Query transformation
- [ ] Hybrid retrieval
- [ ] Reranking
- [ ] Retrieval evaluation
- [ ] Document update and deletion handling
- [ ] Idempotent ingestion pipeline
- [ ] Observability and structured logging
- [ ] Retry and failure handling
- [ ] Rate limiting
- [ ] Authentication
- [ ] API layer
- [ ] Production deployment

---

# Project Goal

The final system will provide a complete RAG pipeline capable of:

1. Ingesting real-world documents
2. Extracting and normalizing content
3. Splitting documents into meaningful chunks
4. Preserving document and chunk metadata
5. Generating semantic embeddings
6. Storing embeddings in PostgreSQL using PGVector
7. Performing semantic similarity search
8. Filtering retrieval using metadata
9. Processing and transforming user queries
10. Constructing relevant context
11. Generating grounded answers using an LLM
12. Returning source references
13. Evaluating retrieval quality
14. Handling document updates and deletion
15. Providing production concerns such as authentication, rate limiting, retries, logging, and observability

The system is being developed step-by-step so that each major component is understood, tested, and integrated before moving to the next.

---

# Architecture

## Target Architecture

```text
                         DOCUMENTS
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Document Loader   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Normalization     │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │      Chunking       │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │      Metadata       │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     Embeddings      │
                  └──────────┬──────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      PostgreSQL + PGVector   │
              │                              │
              │        vector(768)           │
              └──────────────┬───────────────┘
                             │
                        USER QUERY
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Query Processing   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     Retrieval       │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Context Builder   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │        LLM          │
                  │     OpenRouter      │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Answer + Sources   │
                  └─────────────────────┘