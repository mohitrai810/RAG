from typing import Sequence, Set


def hit_rate_at_k(
    retrieved: Sequence[str],
    relevant: Set[str],
    k: int,
) -> float:
    if not relevant or k <= 0:
        return 0.0

    top_k = retrieved[:k]

    return 1.0 if any(item in relevant for item in top_k) else 0.0


def precision_at_k(
    retrieved: Sequence[str],
    relevant: Set[str],
    k: int,
) -> float:
    if k <= 0:
        return 0.0

    top_k = retrieved[:k]

    relevant_retrieved = sum(
        1 for item in top_k if item in relevant
    )

    return relevant_retrieved / k


def recall_at_k(
    retrieved: Sequence[str],
    relevant: Set[str],
    k: int,
) -> float:
    if not relevant or k <= 0:
        return 0.0

    top_k = retrieved[:k]

    retrieved_relevant_ids = set(top_k).intersection(relevant)

    return len(retrieved_relevant_ids) / len(relevant)


def reciprocal_rank(
    retrieved: Sequence[str],
    relevant: Set[str],
) -> float:
    if not relevant:
        return 0.0

    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0