from ..models.payment_method_model import PaymentMethod
from sqlalchemy.future import select
from ..schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodInDB,
)
from ..db.session import get_db


async def create_payment_method(payment_method: PaymentMethodCreate):
    """Creates a new payment method"""
    async with get_db() as session:
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
