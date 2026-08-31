from fastapi import HTTPException
from upstash_redis import Redis
from datetime import date
from app.config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN

redis = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)

DAILY_LIMIT_PER_HOUSEHOLD = 40

def rate_limit_ai_calls(account_id: str) -> None:
    key = f"ai_calls:{account_id}:{date.today().isoformat()}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 60 * 60 * 24)
    if count > DAILY_LIMIT_PER_HOUSEHOLD:
        raise HTTPException(status_code=429, detail="Daily AI call limit reached.")