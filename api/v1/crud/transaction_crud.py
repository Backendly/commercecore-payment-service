from models.transaction_model import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, Dict
from services.stripe_config import stripe
from fastapi import Request, HTTPException
from ..schema.transaction_schema import InitiatePaymentTransaction


async def initiate_payment_transaction(
    payment: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any],
    validated_user: Dict[str, Any],
):
    """Initiates a payment transaction"""
    data = await payment.json()
    order_id = data["order_id"]
    amount = data["amount"]
    account_id = data["account_id"]
    app_id = validated_developer.get("app_id")
    developer_id = validated_developer.get("developer_id")
    user_id = validated_user.get("user_id")
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"],
            metadata={"order_id": order_id, "app_id": app_id},
            stripe_account=account_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the payment intent.{e}",
        )

    new_transaction = Transaction(
        transaction_id=payment_intent["id"],
        order_id=order_id,
        payment_method_id=None,
        developer_id=developer_id,
        user_id=user_id,
        app_id=app_id,
        amount=amount,
        status="pending",
    )

    try:
        session.add(new_transaction)
        await session.commit()
        await session.refresh(new_transaction)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the transaction.{e}",
        )

    return InitiatePaymentTransaction(
        client_secret=payment_intent["client_secret"],
        status=payment_intent["status"],
        transaction_id=new_transaction.transaction_id,
    )


async def payment_confirmation(data: Request, session: AsyncSession):
    """Confirms a payment transaction"""
    data = await data.json()
    transaction_id = data["transaction_id"]
    payment_method_id = data["payment_method_id"]
    account_id = data["account_id"]

    try:
        payment_intent = stripe.PaymentIntent.confirm(
            transaction_id,
            payment_method=payment_method_id,
            stripe_account=account_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while confirming the payment intent{e}"
            f" Check if the payment method is valid, and also check if you have"
            f"completed the onboarding process",
        )

    transaction = (
        await session.execute(
            select(Transaction).filter(Transaction.transaction_id == transaction_id)
        )
    ).scalar()

    transaction.payment_method_id = payment_method_id
    transaction.status = payment_intent["status"]

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while confirming the transaction.{e}",
        )

    return {
        "message": "Payment confirmed successfully",
        "status_code": 200,
        "account_id": account_id,
    }


async def get_transactions(session: AsyncSession, limit: int, offset: int):
    """Gets all transactions"""
    transactions = await session.execute(
        select(Transaction).limit(limit).offset(offset)
    )
    transactions = transactions.scalars().all()
    return transactions
