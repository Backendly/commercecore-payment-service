from ..schema.transaction_schema import (
    InitiatePaymentTransactionResponse,
    ConfirmPaymentTransactionResponse,
    TransactionReturnListing,
    ListingLink,
    ListingMeta,
)
from models.transaction_model import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from ..crud.transaction_crud import (
    initiate_payment_transaction,
    payment_confirmation,
    get_transactions,
)
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import APIRouter, Depends, Request, Query
from db.session import get_db
from typing import Annotated
from fastapi import HTTPException
from fastapi.background import BackgroundTasks
from utils import validate_developer, validate_user
from typing import Dict, Any


router = APIRouter(tags=["Transactions"], prefix="/api/v1")


@router.post(
    "/transactions",
    response_model=InitiatePaymentTransactionResponse,
    status_code=201,
)
async def initiate_transaction(
    payment: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    validated_developer: Dict[str, Any] = Depends(validate_developer),
    validated_user: Dict[str, Any] = Depends(validate_user),
):

    data = await initiate_payment_transaction(
        payment=payment,
        session=session,
        background_tasks=background_tasks,
        validated_developer=validated_developer,
    )
    real_data = data.model_dump()

    links = {
        "self": str(payment.url),
    }
    meta = {
        "message": "Payment initiated successfully",
        "status_code": 201,
    }

    return InitiatePaymentTransactionResponse(links=links, meta=meta, data=real_data)


@router.post("/transactions/confirm", response_model=ConfirmPaymentTransactionResponse)
async def confirm_transaction(data: Request, session: AsyncSession = Depends(get_db)):
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


@router.get("/transactions", response_model=TransactionReturnListing, status_code=200)
async def retrieve_transactions(
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    session: AsyncSession = Depends(get_db),
):
    """Retrieve all transactions"""
    offset = (page - 1) * per_page
    total_items_result = await session.execute(
        select(func.count()).select_from(Transaction)
    )

    total_items = total_items_result.scalar() if total_items_result else 0

    if total_items == 0:
        raise HTTPException(
            status_code=404,
            detail="No transactions found",
        )
    total_pages = (total_items + per_page - 1) // per_page
    data = await get_transactions(session=session, limit=per_page, offset=offset)
    base_url = str(request.url).split("?")[0]

    links = ListingLink(
        prev=f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None,
        self=f"{base_url}?page={page}&per_page={per_page}",
        next=(
            f"{base_url}?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        first=f"{base_url}?page=1&per_page={per_page}",
        last=f"{base_url}?page={total_pages}&per_page={per_page}",
    )
    meta = ListingMeta(
        message="Payment methods retrieved successfully",
        status_code=200,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_items,
    )

    return TransactionReturnListing(links=links, meta=meta, data=data)
