import hashlib
import json
from uuid import UUID

from app.core.redis import redis_client


CACHE_TTL_SECONDS = 900


def build_query_cache_key(
    tenant_id: UUID,
    query: str,
    candidate_k: int,
    final_k: int,
    max_distance: float,
) -> str:
    payload = {
        "tenant_id": str(tenant_id),
        "query": query.strip().lower(),
        "candidate_k": candidate_k,
        "final_k": final_k,
        "max_distance": max_distance,
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()

    return f"rag:query:{digest}"


def get_cached_answer(key: str) -> str | None:
    return redis_client.get(key)


def cache_answer(
    key: str,
    answer: str,
) -> None:
    redis_client.setex(
        key,
        CACHE_TTL_SECONDS,
        answer,
    )

def clear_query_cache() -> None:
    keys = redis_client.scan_iter(
        match="rag:query:*"
    )

    for key in keys:
        redis_client.delete(key)