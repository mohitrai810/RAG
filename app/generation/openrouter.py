import requests

from app.generation.provider import GenerationProvider


class OpenRouterProvider(GenerationProvider):

    def __init__(
        self,
        api_key: str,
        model: str = "openrouter/auto",
    ):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:

        prompt = f"""
Answer the user's question using only the provided context.

If the answer cannot be found in the context, say:
"I don't have enough information in the provided documents to answer that."

Do not use outside knowledge.

Context:
{context}

User question:
{query}
"""

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]