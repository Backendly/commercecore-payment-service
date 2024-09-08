from fastapi import APIRouter, Depends, HTTPException
from crud.payment_method_crud import (
    create_payment_method,
    get_payment_methods,
    get_payment_method,
    update_payment_method,
    delete_payment_method,
)
from schema.payment_method_schema import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodReturn,
    PaymentMethodInDB,
)
from db.session import get_db

router = APIRouter(prefix="/api/v1", tags=["Payment Methods"])


@router.post("/payment-methods", response_model=PaymentMethodReturn)
async def add_payment_method(
    payment_method: PaymentMethodCreate, session=Depends(get_db)
):
    """Creates a new payment method"""
    data = await create_payment_method(payment_method, session=session)
    return {
        "message": "Payment method created successfully",
        "status_code": 201,
        "data": data,
    }
