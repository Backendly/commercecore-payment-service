from db.session import Base
from db.base import ModelBase
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import Column, String, Boolean, JSON, Enum as SQLEnum
from nanoid import generate


def generate_id():
    """Generates a random id"""
    id = f"pm_{str(generate())[:14]}"
    return id


class PaymentMethodType(Enum):
    card = "card"
    paypal = "paypal"
    stripe = "stripe"


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"
    id = Column(String(255), primary_key=True, default=generate_id, index=True)
    is_active = Column(Boolean, default=True)
    method_type = Column(
        SQLEnum(PaymentMethodType, name="payment_method_types"),
        nullable=False,
    )
    details = Column(
        JSON,
        nullable=False,
    )
