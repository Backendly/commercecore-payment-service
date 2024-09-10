from pydantic import BaseModel, model_validator, ValidationError, ValidationInfo
from typing import Optional, Dict, Any
from datetime import datetime
from models.payment_method_model import PaymentMethodType
from pydantic import Field


class PaymentMethodBase(BaseModel):
    method_type: PaymentMethodType
    details: Dict[str, Any]


class PaymentMethodCreate(PaymentMethodBase):
    @model_validator(mode="before")
    @classmethod
    def check_for_required_details(cls, values):
        details = values.get("details")
        method_type = values.get("method_type")
        if method_type == "card":
            required_fields = [
                "card_number",
                "expiry_month",
                "expiry_year",
                "card_cvc",
                "card_type",
            ]
            for field in required_fields:
                if field not in details.keys():
                    raise ValueError(f"{field} is required for card payment")
        return values


class PaymentMethodInDB(PaymentMethodBase):
    id: str
    created_at: datetime = Field
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
