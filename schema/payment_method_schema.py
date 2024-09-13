from pydantic import BaseModel, model_validator, ValidationError, ValidationInfo
from typing import Optional, Dict, Any
from datetime import datetime
from models.payment_method_model import PaymentMethodType
import re


class PaymentMethodBase(BaseModel):
    type: PaymentMethodType
    details: Dict[str, Any]


class PaymentMethodCreate(PaymentMethodBase):
    @model_validator(mode="before")
    @classmethod
    def check_for_required_details(cls, values):
        details = values.get("details")
        if not details:
            raise ValueError("details is required")
        type = values.get("type")
        if not type:
            raise ValueError("method_type is required")
        if type == "card":
            required_fields = [
                "card_number",
                "exp_month",
                "exp_year",
                "card_cvc",
            ]
            for field in required_fields:
                if field not in details.keys():
                    raise ValueError(f"{field} is required for card payment")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_expiry_date(cls, values):
        details = values.get("details")
        if not details:
            raise ValueError("details is required")
        type = values.get("type")
        if type == "card" and details.get("expiry_date") is not None:
            expiry_date = details.get("expiry_date")
            if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry_date):
                raise ValueError("expiry_date must be in MM/YY format")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_card_number(cls, values):
        details = values.get("details")
        if not details:
            raise ValueError("details is required")
        type = values.get("type")
        if not details.get("card_number"):
            raise ValueError("card_number is required for card payment")

        if type == "card" and details.get("card_number") is not None:
            card_number = details.get("card_number")
            if card_number and not card_number.isdigit():
                raise ValueError("card_number must be all digits")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_card_number_length(cls, values):
        details = values.get("details")
        if not details:
            raise ValueError("details is required")
        if not details.get("card_number"):
            raise ValueError("card_number required for card payment")
        type = values.get("type")
        if type == "card" and details.get("card_number") is not None:
            card_number = details.get("card_number")
            if card_number and (
                len(str(card_number)) < 13 or len(str(card_number)) > 19
            ):
                raise ValueError("card_number must be between 13 and 19 digits")
        return values


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
