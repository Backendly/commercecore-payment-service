from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from models.payment_method_model import PaymentMethodType


class PaymentMethodBase(BaseModel):
    is_active: Optional[bool] = True
    method_type: PaymentMethodType
    details: Dict[str, Any]


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(PaymentMethodBase):
    pass


class PaymentMethodInDB(PaymentMethodBase):
    id: str
    created_at: datetime
    updated_at: datetime

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
    prev: str
    self: str
    next: str


class PaymentMethodReturnListing(BaseModel):
    links: ListingLink
    meta: ListingMeta
    data: list[PaymentMethodInDB]
