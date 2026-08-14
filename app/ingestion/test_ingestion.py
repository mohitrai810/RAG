from app.ingestion.service import ingest


if __name__ == "__main__":
    ingest("data/documents/test.md")