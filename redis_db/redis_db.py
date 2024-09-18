import redis
import aioredis


class CustomRedis:
    """Class Implementing Redis configuration"""

    def __init__(self, redis):
        self.redis_client = redis

    @classmethod
    async def create(cls, redis_url: str):
        redis = await aioredis.from_url(redis_url)
        return cls(redis)

    async def set(self, key: str, value, expire: int = 3600):
        await self.redis_client.set(key, value, expire=expire)

    async def get(self, key: str):
        return await self.redis_client.get(key)

    async def delete(self, key: str):
        await self.redis_client.delete(key)

    async def exists(self, *keys):
        existing_keys = []
        for key in keys:
            if await self.redis_client.exists(key):
                existing_keys.append(key)
        return existing_keys


redis_instance = CustomRedis("redis://localhost")
