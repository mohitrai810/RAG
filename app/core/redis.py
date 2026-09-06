from redis import Redis

from app.core.config import get_settings


settings = get_settings()

redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)