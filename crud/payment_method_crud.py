from models.payment_method_model import PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodInDB,
    PaymentMethodType,
)


async def create_payment_method(
    payment_method: PaymentMethodCreate, session: AsyncSession
):
    """Creates a new payment method"""
    payment_method_dict = payment_method.model_dump()
    if payment_method_dict.get("method_type") is PaymentMethodType.card:
        card = payment_method_dict.get("details").get("card_number")
        if card:
            smt = select(PaymentMethod).filter(
                PaymentMethod.details["card_number"] == card
            )
            result = await session.execute(smt)
            payment_method_db = result.scalars().first()
            if payment_method_db:
                raise HTTPException(
                    status_code=400,
                    detail=f"Card already exists",
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

    result = new_payment_method
    result = PaymentMethodInDB.model_validate(result)
    result = result.model_dump()
    del result["details"]["card_cvc"]
    result["details"]["card_last_four"] = result["details"]["card_number"][-4:]
    del result["details"]["card_number"]

    return PaymentMethodInDB(**result)


async def get_payment_methods(session: AsyncSession, limit: int, offset: int):
    """Returns all payment methods"""
    result = await session.execute(select(PaymentMethod).limit(limit).offset(offset))
    results = result.scalars().all()
    new_results = []
    for result in results:
        result = PaymentMethodInDB.model_validate(result)
        result = result.model_dump()
        del result["details"]["card_cvc"]
        result["details"]["card_last_four"] = result["details"]["card_number"][-4:]
        del result["details"]["card_number"]
        new_results.append(result)

    return new_results


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
    result = payment_method
    result = PaymentMethodInDB.model_validate(result)
    result = result.model_dump()
    del result["details"]["card_cvc"]
    result["details"]["card_last_four"] = result["details"]["card_number"][-4:]
    del result["details"]["card_number"]

    return PaymentMethodInDB(**result)


async def delete_payment_method(id: str, session: AsyncSession):
    """Deletes a payment method"""
    payment_method = await get_payment_method(id, session)
    if not payment_method:
        raise HTTPException(
            status_code=404,
            detail="Payment method not found",
        )
    payment_method = await session.execute(
        select(PaymentMethod).filter(PaymentMethod.id == id)
    )
    payment_method = payment_method.scalars().first()
    await session.delete(payment_method)
    await session.commit()
