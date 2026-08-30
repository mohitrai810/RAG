# Technical Troubleshooting Corpus

An original, reproducible corpus for testing technical-document retrieval and RAG pipelines.

## Contents

- Fifteen Markdown runbooks covering Redis, PostgreSQL, Docker, FastAPI, and Linux
- Sixty troubleshooting cases with stable evidence IDs
- Forty verified question-to-evidence labels
- Reference answers for later end-to-end evaluation
- SHA-256 document hashes in `manifest.json`

## Ground-truth design

Database chunk UUIDs can change after every ingestion. Evaluation therefore labels stable evidence IDs such as `KB-REDIS-001`. After chunking, associate a retrieved chunk with every evidence ID appearing in its content. A hit occurs when the retrieved results contain an expected evidence ID.

## Suggested ingestion settings

Start with chunk size 800 and overlap 150. Record the exact settings with every experiment. Chunk counts vary by splitter implementation and separator behavior.

## Evaluation order

1. Ingest every document.
2. Build the map from stored chunks to contained evidence IDs.
3. Run every query using vector retrieval only.
4. Run the same queries using vector retrieval plus reranking.
5. Compare HitRate@K, Recall@K, MRR, and latency.

## Important limitation

This is a synthetic operations corpus. It is suitable for reproducible engineering experiments, but results should not be generalized to every enterprise knowledge base. Add a second real, license-compatible corpus later.

## License

CC0-1.0. You may commit, modify, and redistribute this corpus.
