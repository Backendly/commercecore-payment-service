from redis_db.redis_db import redis_instance


def store_user_data(key: str, value: str):
    """Store user data in Redis"""
    redis_instance.set(key, value)


def store_developer_data(key: str, value: str):
    """Store developer data in Redis"""
    redis_instance.set(key, value)
