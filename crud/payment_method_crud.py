from models.payment_method_model import PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from sqlalchemy.future import select
from schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodInDB,
)
from db.session import get_db


async def create_payment_method(
    payment_method: PaymentMethodCreate, session: AsyncSession
):
    """Creates a new payment method"""

    if payment_method.method_type == "card":
        card_details = payment_method.details
        required_fields = ["card_number", "cvv", "expiry_date"]

        for field in required_fields:
            if field not in card_details:
                raise HTTPException(
                    status_code=400,
                    detail=f"Payment method details must contain a {field} field",
                )

    new_payment_method = PaymentMethod(**payment_method.model_dump())

    try:
        session.add(new_payment_method)
        await session.commit()
        await session.refresh(new_payment_method)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the payment method.{e}",
        )

    return new_payment_method


async def get_payment_methods(session: AsyncSession, limit: int, offset: int):
    """Returns all payment methods"""
    result = await session.execute(select(PaymentMethod).limit(limit).offset(offset))
    return result.scalars().all()


async def get_payment_method(id: str, session: AsyncSession):
    """Returns a payment method by id"""
    result = await session.execute(
        select(PaymentMethod).filter(PaymentMethod.id == id),
    )
    payment_method = result.scalars().first()
    if not payment_method:
        raise HTTPException(
            status_code=404,
            detail="Payment method not found",
        )
    return payment_method


async def delete_payment_method(id: str):
    """Deletes a payment method"""
    async with get_db() as session:
        result = await session.execute(
            select(PaymentMethod).filter(PaymentMethod.id == id)
        )
        if not result.scalars().first():
            raise HTTPException(
                status_code=404,
                detail="Payment method not found",
            )
        payment_method = result.scalar_one()
        session.delete(payment_method)
        await session.commit()
        return payment_method
