from models.payment_method_model import PaymentMethod
from services.stripe_config import stripe
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
    payment_method_type = payment_method_dict["type"]
    payment_method_details = payment_method_dict["details"]

    if payment_method_type == PaymentMethodType.card:
        try:
            payment_method_stripe = await stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": payment_method_details["card_number"],
                    "exp_month": payment_method_details["exp_month"],
                    "exp_year": payment_method_details["exp_year"],
                    "cvc": payment_method_details["card_cvc"],
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while creating the payment method.{e}",
            )
        new_payment_method = PaymentMethod(
            id=payment_method_stripe["id"],
            type=payment_method_type,
            details={
                "card_last_four": payment_method_stripe["last4"],
                "card_type": payment_method_stripe["brand"],
                "exp_month": payment_method_stripe["exp_month"],
                "exp_year": payment_method_stripe["exp_year"],
            },
        )

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
