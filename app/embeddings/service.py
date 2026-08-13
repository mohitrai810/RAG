from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self,model_name):
        self.model = SentenceTransformer(model_name)

    def embed_sentences(self,texts):
        embed = self.model.encode(texts,normalize_embeddings=True)

        return embed.tolist()

    def embed_query(self,texts):
            embed = self.model.encode(texts,normalize_embeddings=True)
    
            return embed.tolist()

    @property
    def dimension(self):
         return self.model.get_sentence_embedding_dimension()