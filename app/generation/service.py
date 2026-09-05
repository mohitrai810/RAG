from app.generation.provider import GenerationProvider
class GenerationService:

    def __init__(self, provider: GenerationProvider):
        self.provider = provider

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        if not context.strip():
            return "I couldn't find relevant information in the provided documents."

        return self.provider.generate(
            query=query,
            context=context,
        )