from types import SimpleNamespace

from app.reranking.flashrank import FlashRankReranker


def main():
    results = [
        (
            SimpleNamespace(
                content="Redis is an in-memory key-value database."
            ),
            0.20,
        ),
        (
            SimpleNamespace(
                content="Redis AOF persistence replays logged commands during startup to recover data."
            ),
            0.35,
        ),
        (
            SimpleNamespace(
                content="Redis can also persist data using RDB snapshots."
            ),
            0.25,
        ),
    ]

    reranker = FlashRankReranker()

    reranked = reranker.rerank(
        query="How does Redis recover using AOF?",
        results=results,
        top_k=3,
    )

    for index, (chunk, distance) in enumerate(reranked, start=1):
        print(f"{index}. distance={distance}")
        print(chunk.content)
        print()


if __name__ == "__main__":
    main()