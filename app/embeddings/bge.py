from sentence_transformers import SentenceTransformer

from app.embeddings.provider import EmbeddingProvider


class BGEEmbeddingProvider(EmbeddingProvider):

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    @property
    def dimensions(self) -> int:
        return self.model.get_sentence_embedding_dimension()