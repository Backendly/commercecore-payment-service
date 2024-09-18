from ..schema.refunds_schema import RefundCreate, RefundInDB, RefundReturnDetail
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from models.refunds_model import Refund
from fastapi import Request
from services.stripe_config import stripe
from models.transaction_model import Transaction
from typing import Dict, Any


async def create_refund(
    refund: Request,
    session: AsyncSession,
    validated_developer: Dict[str, Any],
    validated_user: Dict[str, Any],
):
    """Creates a refund"""
    data = await refund.json()
    order_id = data["order_id"]
    account_id = data["account_id"]
    app_id = validated_developer.get("app_id")

    transaction = await session.execute(
        select(Transaction).where(Transaction.order_id == order_id)
    )
    real_transaction = transaction.scalars().first()
    if not real_transaction:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with order_id {order_id} found.",
        )

    transaction_id = real_transaction.transaction_id

    try:
        refund_stripe = stripe.Refund.create(
            payment_intent=transaction_id,
            stripe_account=account_id,
            metadata={"order_id": order_id, "app_id": app_id},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the refund. {e}",
        )

    new_refund = Refund(
        refund_id=refund_stripe["id"],
        transaction_id=transaction_id,
        user_id=real_transaction.user_id,
        order_id=order_id,
        app_id=app_id,
        amount=refund_stripe["amount"],
        status=refund_stripe["status"],
        reason=refund_stripe["reason"],
    )
    try:
        session.add(new_refund)
        await session.commit()
        await session.refresh(new_refund)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the refund.{e}",
        )

    return new_refund
