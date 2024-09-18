from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from models.payment_method_model import PaymentMethod
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Annotated
from ..crud.payment_method_crud import (
    create_payment_method,
    get_payment_methods,
    get_payment_method,
    delete_payment_method,
)
from utils import validate_developer, validate_user
from ..schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodInDB,
    PaymentMethodReturnDetail,
    PaymentMethodReturnListing,
    ListingLink,
    ListingMeta,
)
from db.session import get_db

router = APIRouter(prefix="/api/v1", tags=["Payment Methods"])


@router.post(
    "/payment-methods",
    response_model=PaymentMethodReturnDetail,
    status_code=201,
)
async def add_payment_method(
    request: Request,
    payment_method: PaymentMethodCreate,
    session: AsyncSession = Depends(get_db),
):
    """Creates a new payment method"""
    data = await create_payment_method(payment_method, session=session)
    self_link = str(request.url_for("retrieve_payment_method", id=data.id))
    return {
        "data": data,
        "meta": {
            "message": "Payment method created successfully",
            "status_code": 201,
        },
        "links": {
            "self": self_link,
        },
    }


@router.get("/payment-methods", response_model=PaymentMethodReturnListing)
async def retrieve_payment_methods(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    session: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Retrieve all user"""
    offset = (page - 1) * per_page
    total_items_result = await session.execute(
        select(func.count()).select_from(PaymentMethod)
    )
    total_items = total_items_result.scalar() if total_items_result else 0

    if total_items == 0:
        raise HTTPException(
            status_code=404,
            detail="No payment methods found",
        )
    total_pages = (total_items + per_page - 1) // per_page

    data = await get_payment_methods(session=session, limit=per_page, offset=offset)

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

    return PaymentMethodReturnListing(links=links, meta=meta, data=data)


@router.get("/payment-methods/{id}", response_model=PaymentMethodReturnDetail)
async def retrieve_payment_method(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_db),
):
    """Retrieves a payment method"""
    data = await get_payment_method(id=id, session=session)
    self_link = str(request.url_for("retrieve_payment_method", id=data.id))
    return {
        "data": data,
        "meta": {
            "message": "Payment method retrieved successfully",
            "status_code": 200,
        },
        "links": {
            "self": self_link,
        },
    }


@router.delete("/payment-methods/{id}")
async def remove_payment_method(
    id: str,
    session: AsyncSession = Depends(get_db),
):
    """Deletes a payment method"""
    await delete_payment_method(id=id, session=session)
    return {
        "message": "Payment method deleted successfully",
        "status_code": 200,
    }
