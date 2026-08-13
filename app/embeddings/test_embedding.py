from app.embeddings.service import EmbeddingService

MODEL_NAME = "BAAI/bge-base-en-v1.5"

def main():
    service = EmbeddingService(MODEL_NAME)

    text = "Redis AOF logs write operations for persistence."
    embedding = service.embed_query(text)
    print("Dimension :",len(embedding))
    print("Model Dimension :",service.dimension)
    print("First 5 dimension :",embedding[:5])

if __name__ == "__main__":
    main()