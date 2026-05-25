import redis
import json
from app.core.config import settings

# Single connection pool shared across the app
_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=10
)

def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


JOB_TTL = 60 * 60 * 2   # jobs expire after 2 hours


def set_job(job_id: str, data: dict) -> None:
    r = get_redis()
    # image_bytes can't serialize to JSON — store separately as bytes
    image_bytes = data.pop("image_bytes", None)
    r.set(f"job:{job_id}", json.dumps(data), ex=JOB_TTL)
    if image_bytes:
        r.set(f"job:{job_id}:image", image_bytes, ex=JOB_TTL)


def get_job(job_id: str) -> dict | None:
    r = get_redis()
    raw = r.get(f"job:{job_id}")
    if not raw:
        return None
    return json.loads(raw)


def update_job(job_id: str, updates: dict) -> None:
    r = get_redis()
    raw = r.get(f"job:{job_id}")
    if not raw:
        return
    data = json.loads(raw)
    # Never overwrite image_bytes via update
    updates.pop("image_bytes", None)
    data.update(updates)
    r.set(f"job:{job_id}", json.dumps(data), ex=JOB_TTL)


def append_event(job_id: str, event: dict) -> None:
    r = get_redis()
    r.rpush(f"job:{job_id}:events", json.dumps(event))
    r.expire(f"job:{job_id}:events", JOB_TTL)


def get_events(job_id: str) -> list[dict]:
    r = get_redis()
    raw_list = r.lrange(f"job:{job_id}:events", 0, -1)
    return [json.loads(e) for e in raw_list]


def set_image_bytes(job_id: str, image_bytes: bytes) -> None:
    """Store raw image bytes using a separate non-decoding connection."""
    raw_r = redis.Redis.from_url(settings.redis_url, decode_responses=False)
    raw_r.set(f"job:{job_id}:image", image_bytes, ex=JOB_TTL)


def get_image_bytes(job_id: str) -> bytes | None:
    """Retrieve raw image bytes using a separate non-decoding connection."""
    raw_r = redis.Redis.from_url(settings.redis_url, decode_responses=False)
    return raw_r.get(f"job:{job_id}:image")