import json
import time
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

        max_attempts = 3

        for attempt in range(max_attempts):
            try:
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
                    timeout=(5, 45),
                )

                if response.status_code == 429:
                    if attempt == max_attempts - 1:
                        raise RuntimeError(
                            "LLM rate limit exceeded after retries."
                        )

                    time.sleep(2**attempt)
                    continue

                if 500 <= response.status_code < 600:
                    if attempt == max_attempts - 1:
                        raise RuntimeError(
                            f"LLM provider failed after retries: "
                            f"{response.status_code}"
                        )

                    time.sleep(2**attempt)
                    continue

                response.raise_for_status()

                data = response.json()

                return data["choices"][0]["message"]["content"]

            except requests.Timeout:
                if attempt == max_attempts - 1:
                    raise RuntimeError("LLM request timed out after retries.")

                time.sleep(2**attempt)

            except requests.ConnectionError:
                if attempt == max_attempts - 1:
                    raise RuntimeError(
                        "Could not connect to LLM provider after retries."
                    )

                time.sleep(2**attempt)

        raise RuntimeError("LLM request failed.")

    def stream_generate(
        self,
        query: str,
        context: str,
    ):
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
                "stream": True,
            },
            stream=True,
            timeout=(5, 45),
        )

        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            if not line.startswith("data: "):
                continue

            data = line[6:]

            if data == "[DONE]":
                break

            chunk = json.loads(data)

            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")

            if delta:
                yield delta