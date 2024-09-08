from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class PaymentMethodType(Enum):
    card = "card"
    paypal = "paypal"
    stripe = "stripe"


class PaymentMethodBase(BaseModel):
    is_active: Optional[bool] = True
    method_type: PaymentMethodType
    details: Dict[str, Any]


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(PaymentMethodBase):
    pass


class PaymentMethodInDB(PaymentMethodBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
