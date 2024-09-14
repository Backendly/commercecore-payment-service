from pydantic import BaseModel
from typing import Optional, Dict, Any


class RefundBase(BaseModel):
    refund_id: str
    transaction_id: str
    user_id: str
    order_id: str
    app_id: str
    amount: str
    status: str
    reason: Optional[str]


class RefundCreate(RefundBase):
    pass


class RefundInDB(RefundBase):

    class Config:
        from_attributes = True


class RefundReturnDetail(BaseModel):
    meta: Dict[str, Any]
    data: RefundInDB
    links: Dict[str, Any]


class ListingMeta(BaseModel):
    message: str
    status_code: int
    page: int
    per_page: int
    total_pages: int
    total_items: int


class ListingLink(BaseModel):
    prev: Optional[str]
    self: str
    next: Optional[str]
    first: str
    last: str


class RefundReturnListing(BaseModel):
    meta: ListingMeta
    data: list[RefundInDB]
    links: ListingLink
