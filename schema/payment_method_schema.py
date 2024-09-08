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
