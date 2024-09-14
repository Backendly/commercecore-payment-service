from pydantic import BaseModel
from typing import Optional, Dict, Any
from models.transaction_model import Transaction


class TransactionBase(BaseModel):
    transaction_id: str | None
    user_id: str | None
    order_id: str | None
    payment_method_id: str | None
    app_id: str | None
    developer_id: str | None
    amount: str | None
    status: str | None


class TransactionCreate(TransactionBase):
    pass


class TransactionInDB(TransactionBase):

    class Config:
        from_attributes = True


class TransactionReturnDetail(BaseModel):
    meta: Dict[str, Any]
    data: TransactionInDB
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


class TransactionReturnListing(BaseModel):
    meta: ListingMeta
    data: list[TransactionInDB]
    links: ListingLink


class InitiatePaymentTransaction(BaseModel):
    client_secret: str
    status: str
    transaction_id: str


class InitiatePaymentTransactionResponse(BaseModel):
    data: Dict[str, Any]
    meta: Dict[str, Any]
    links: Dict[str, Any]


class ConfirmPaymentTransactionResponse(InitiatePaymentTransactionResponse):
    pass


class ConnectedAccountResponse(InitiatePaymentTransactionResponse):
    pass


class InitiatePaymentCreate(BaseModel):
    order_id: str
