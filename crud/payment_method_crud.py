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
    new_payment_method = PaymentMethod(**payment_method.model_dump())
    session.add(new_payment_method)
    await session.commit()
    await session.refresh(new_payment_method)
    return new_payment_method


async def get_payment_methods():
    """Returns all payment methods"""
    async with get_db() as session:
        result = await session.execute(select(PaymentMethod))
        return result.scalars().all()


async def get_payment_method(id: str):
    """Returns a payment method by id"""
    async with get_db() as session:
        result = await session.execute(
            select(PaymentMethod).filter(PaymentMethod.id == id)
        )
        return result.scalar_one()


async def update_payment_method(id: str, payment_method: PaymentMethodUpdate):
    """Updates a payment method"""
    async with get_db() as session:
        result = await session.execute(
            select(PaymentMethod).filter(PaymentMethod.id == id)
        )
        if not result.scalars().first():
            raise HTTPException(
                status_code=404,
                detail="Payment method not found",
            )
        payment_method_db = result.scalar_one()
        for key, value in payment_method.model_dump().items():
            setattr(payment_method_db, key, value)
        await session.commit()
        await session.refresh(payment_method_db)
        return payment_method_db


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