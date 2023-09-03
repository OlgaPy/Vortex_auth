# import redis.asyncio as redis
import redis

from app.core.settings import get_redis_url
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# async \
def get_redis():
    redis_client = redis.from_url(get_redis_url())
    try:
        yield redis_client
    finally:
        # await
        redis_client.close()
