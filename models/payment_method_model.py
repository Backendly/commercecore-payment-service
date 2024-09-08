from ..db.session import Base
from ..db.base import ModelBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Enum
from datetime import datetime
from uuid import uuid4


def generate_id():
    """Generates a random id"""
    id = f"pm_{str(uuid4())[:8]}"


class PaymentMethodType(Enum):
    card = "card"
    paypal = "paypal"
    stripe = "stripe"


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"
    id = Column(String, primary_key=True, default=generate_id, index=True)
    is_active = Column(Boolean, default=True)
    method_type = Column(
        Enum(PaymentMethodType, name="payment_method_types"),
        nullable=False,
    )
    details = Column(
        JSON,
        nullable=False,
    )
