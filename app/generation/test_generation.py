from app.core.config import get_settings
from app.generation.openrouter import OpenRouterProvider
from app.generation.service import GenerationService

if __name__ == "__main__":
    settings = get_settings()

    provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key,
    )

    service = GenerationService(provider)

    answer = service.generate(
        query="What is AOF? and some more about virat kohli",
        context="""
AOF stands for Append Only File.

Instead of periodically saving the complete dataset,
Redis records write operations.
""",
    )

    print("\n===== ANSWER =====\n")
    print(answer)