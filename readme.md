# Production RAG System

A production-oriented Retrieval-Augmented Generation (RAG) system built from scratch to understand and implement reliable document ingestion, semantic search, vector retrieval, and grounded LLM generation.

This project is being developed incrementally with a strong focus on **production backend engineering, retrieval quality, observability, and understanding the systems behind RAG** rather than building a basic "chat with PDF" demo.

---

##  Project Goal

The goal is to build a complete RAG pipeline capable of:

- Ingesting real-world documents
- Extracting and normalizing content
- Splitting documents into meaningful chunks
- Preserving useful metadata
- Generating semantic embeddings
- Storing embeddings in PostgreSQL using PGVector
- Performing semantic similarity search
- Filtering retrieval using metadata
- Constructing relevant context for an LLM
- Generating grounded answers
- Returning source references
- Evaluating retrieval quality
- Handling document updates and deletion
- Eventually supporting production concerns such as authentication, rate limiting, logging, retries, and observability

The project is intentionally being built step-by-step so that every major component is understood and tested before moving to the next.

---

#  Architecture

The target architecture is:

```text
                    DOCUMENTS
                       │
                       ▼
              ┌─────────────────┐
              │ Document Loader  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Normalization   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Chunking      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Metadata      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Embeddings     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────────────┐
              │ PostgreSQL + PGVector   │
              └────────────┬────────────┘
                           │
                     USER QUERY
                           │
                           ▼
              ┌─────────────────┐
              │ Query Processing │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Retrieval     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Context Builder  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │       LLM        │
              │    OpenRouter    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Answer + Sources │
              └─────────────────┘