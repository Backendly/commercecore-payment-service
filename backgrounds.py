from redis_db.redis_db import redis_instance
from models.transaction_model import Transaction


async def store_user_data(key: str, value: str):
    """Store user data in Redis"""
    await redis_instance.set(key, value)


async def store_developer_data(key: str, value: str):
    """Store developer data in Redis"""
    await redis_instance.set(key, value)


def save_transaction(transaction: Transaction):
    """Save transaction in Redis"""
    redis_instance.set(transaction.transaction_id, transaction)
