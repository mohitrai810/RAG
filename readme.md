# Production RAG System

A production-oriented Retrieval-Augmented Generation (RAG) system designed to explore reliable document retrieval, semantic search, and grounded LLM generation.

The project is being built incrementally with a focus on understanding the underlying systems rather than creating a simple "chat with PDF" application.

## Overview

The system follows a modular RAG architecture:

```text
Documents
    |
    v
Document Ingestion
    |
    v
Text Extraction & Normalization
    |
    v
Document Chunking
    |
    v
Embedding Generation
    |
    v
PostgreSQL + PGVector
    |
    v
Semantic Retrieval
    |
    v
Context Construction
    |
    v
LLM Generation
    |
    v
Answer + Source References