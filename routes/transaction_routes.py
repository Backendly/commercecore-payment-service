from schema.transaction_schema import (
    InitiatePaymentTransactionResponse,
    ConfirmPaymentTransactionResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from crud.transaction_crud import (
    initiate_payment_transaction,
    payment_confirmation,
    create_connected_account,
    continue_onboarding,
)
from fastapi import APIRouter, Depends, Request
from db.session import get_db


router = APIRouter(tags=["Transactions"], prefix="/api/v1")


@router.post(
    "/payments/initiate",
    response_model=InitiatePaymentTransactionResponse,
    status_code=201,
)
async def initiate_payment(payment: Request, session: AsyncSession = Depends(get_db)):
    data = await initiate_payment_transaction(payment=payment, session=session)
    real_data = data.model_dump()

    links = {
        "self": str(payment.url),
    }
    meta = {
        "message": "Payment initiated successfully",
        "status_code": 201,
    }

    return InitiatePaymentTransactionResponse(links=links, meta=meta, data=real_data)


@router.post("/payments/confirm", response_model=ConfirmPaymentTransactionResponse)
async def confirm_payment(data: Request, session: AsyncSession = Depends(get_db)):
    """Confirms a payment transaction"""
    data_response = await payment_confirmation(data=data, session=session)

    links = {
        "self": str(data.url),
    }
    meta = {
        "message": "Payment confirmed successfully",
        "status_code": 200,
    }

    return ConfirmPaymentTransactionResponse(links=links, data=data_response, meta=meta)
