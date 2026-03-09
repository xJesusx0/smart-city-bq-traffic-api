import redis

from app.core.settings import settings


def get_redis_client():
    return redis.from_url(settings.redis_url, decode_responses=True)
