from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from models.payment_method_model import PaymentMethod
from fastapi import HTTPException
from fastapi.background import BackgroundTasks
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Annotated
from utils import validate_developer, validate_user, validate_app
from db.session import get_db
from ..crud.payment_method_crud import create_payment_method
from ..schema.payment_method_schema import PaymentMethodReturnDetail

router = APIRouter(prefix="/api/v1", tags=["Payment Methods"])


@router.post("/payment-methods", status_code=201)
async def add_payment_method(
    data: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    """Adds a new payment method"""
    validated_developer = await validate_developer(
        data, background_tasks=background_tasks
    )
    validated_user = await validate_user(data, background_tasks=background_tasks)
    validated_app = await validate_app(data, background_tasks=background_tasks)
    payment_method = await create_payment_method(
        data=data,
        session=session,
        validated_app=validated_app,
        validated_developer=validated_developer,
        validated_user=validated_user,
    )
    return PaymentMethodReturnDetail(
        links={"self": str(data.url)},
        data=payment_method,
        meta={"status_code": 201},
    )
