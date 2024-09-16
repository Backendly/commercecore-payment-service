from ..schema.refunds_schema import RefundCreate, RefundInDB, RefundReturnDetail
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from models.refunds_model import Refund
from fastapi import Request
from services.stripe_config import stripe
from models.transaction_model import Transaction


async def create_refund(refund: Request, session: AsyncSession):
    """Creates a refund"""
    data = await refund.json()
    order_id = data["order_id"]
    app_id = data["app_id"]
    account_id = data["account_id"]

    transaction = await session.execute(
        select(Transaction).where(Transaction.order_id == order_id)
    )
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    transaction = transaction.scalars().first()
    transaction_id = transaction.transaction_id

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
        user_id=transaction.user_id,
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
