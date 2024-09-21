import os
import redis


class CustomRedis:
    """Class Implementing Redis configuration"""

    def __init__(self):
        REDIS_URL = os.getenv("REDIS_URL")
        self.client_url = redis.Redis.from_url(REDIS_URL)

    def set(self, key: str, value, expire: int = 3600):
        self.client_url.set(key, value, ex=expire)

    def get(self, key: str):
        return self.client_url.get(key)

    def delete(self, key: str):
        self.client_url.delete(key)

    def exists(self, *keys):
        existing_keys = []
        for key in keys:
            if self.client_url.exists(key):
                existing_keys.append(key)
        return existing_keys

    def publish(self, channel: str, message: str):
        self.client_url.publish(channel, message)
