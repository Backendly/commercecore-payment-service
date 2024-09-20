from models.transaction_model import Transaction
from api.v1.schema.transaction_schema import InitiatePaymentTransaction
from db.session import redis_instance
from db.session import get_db
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def store_user_data(key: str, value: str):
    """Store user data in Redis"""
    client = redis_instance()
    client.set(key, value)
    print(client.get(key))


async def store_developer_data(key: str, value: str):
    """Store developer data in Redis"""
    client = redis_instance()
    client.set(key, value)
    print(client.get(key))


async def save_transaction(payment, payment_intent: dict, session: AsyncSession):
    """Save transaction in Redis"""
    new_transaction = Transaction(
        transaction_id=payment_intent["id"],
        order_id=payment_intent.get("metadata").get("order_id"),
        payment_method_id=None,
        developer_id=payment_intent.get("metadata").get("developer_id"),
        user_id=payment.headers.get("X-User-ID"),
        app_id=payment_intent.get("metadata").get("app_id"),
        amount=payment_intent.get("amount"),
        status="pending",
    )

    try:
        session.add(new_transaction)
        await session.commit()
        await session.refresh(new_transaction)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the transaction.{e}",
        )
