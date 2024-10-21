from pydantic import BaseModel, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from models.payment_method_model import PaymentMethodType
import re


class PaymentMethodBase(BaseModel):
    payment_method_id: str
    type: str
    preferred: bool


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodInDB(PaymentMethodBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class PaymentMethodReturnDetail(BaseModel):
    data: PaymentMethodInDB
    meta: Optional[Dict[str, Any]]
    links: Optional[Dict[str, Any]]


class ListingMeta(BaseModel):
    message: str
    status_code: int
    page: int
    per_page: int
    total_pages: int
    total_items: int


class ListingLink(BaseModel):
    prev: str | None
    self: str
    next: str | None
    first: str
    last: str


class PaymentMethodReturnListing(BaseModel):
    links: ListingLink
    meta: ListingMeta
    data: list[PaymentMethodInDB]


class InitiatePaymentTransaction(BaseModel):
    order_details: Dict[str, Any]
    payment_method_id: str
    developer_id: str
