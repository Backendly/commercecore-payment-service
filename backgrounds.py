from models.transaction_model import Transaction

from api.v1.schema.transaction_schema import InitiatePaymentTransaction
from db.session import redis_instance


async def store_user_data(key: str, value: str):
    """Store user data in Redis"""
    client = await redis_instance()
    await client.set(key, value)


async def store_developer_data(key: str, value: str):
    """Store developer data in Redis"""
    client = await redis_instance()
    await client.set(key, value)


async def save_transaction(transaction: Transaction):
    """Save transaction in Redis"""
    transaction_dict = transaction.model
