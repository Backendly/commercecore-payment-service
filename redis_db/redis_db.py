import aioredis
import os


class CustomRedis:
    """Class Implementing Redis configuration"""

    def __init__(self, client_url):
        self.client_url = client_url
        self.redis_client = None

    async def initialize(self):
        self.redis_client = await aioredis.from_url(self.client_url)

    async def set(self, key: str, value, expire: int = 3600):
        await self.redis_client.set(key, value, ex=expire)

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
