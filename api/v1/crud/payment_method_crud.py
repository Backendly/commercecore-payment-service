from models.payment_method_model import PaymentMethod
from services.stripe_config import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request
from sqlalchemy.future import select
from typing import Dict


async def create_payment_method(
    data: Request,
    session: AsyncSession,
    validated_developer: Dict | str,
    validated_user: Dict | str,
    validated_app: Dict | str,
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
    payment_method_dict = await data.json()
    payment_method_type = payment_method_dict.get("type")
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
