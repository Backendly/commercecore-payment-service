from models.payment_method_model import PaymentMethod
from services.stripe_config import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request
from sqlalchemy.future import select
from ..schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodInDB,
    PaymentMethodType,
)


async def create_payment_method(
    payment_method: Request,
    session: AsyncSession,
    validated_developer: dict,
    validated_user: dict,
    validated_app: dict,
):
    """Creates a new payment method"""
    developer_id = (
        validated_developer.get("developer_id")
        if type(validated_developer) == dict
        else validated_developer
    )
    user_id = (
        validated_user.get("user_id")
        if type(validated_user) == dict
        else validated_user
    )
    app_id = (
        validated_app.get("app_id") if type(validated_app) == dict else validated_app
    )

    payment_method_dict = payment_method.json()
    payment_method_type = payment_method_dict["type"]
    preffered = payment_method_dict.get("preferred", False)
    payment_method_id = payment_method_dict.get("payment_method_id", None)

    new_payment_method = PaymentMethod(
        payment_method_id=payment_method_id,
        user_id=user_id,
        app_id=app_id,
        developer_id=developer_id,
        type=payment_method_type,
        preferred=preffered,
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
