from ..db.session import Base
from ..db.base import ModelBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Enum
from datetime import datetime


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"

    is_active = Column(Boolean, default=True)
    method_type = Column(
        Enum("card", "paypal", "stripe", name="payment_method_types"),
        nullable=False,
    )
    details = Column(
        JSON,
        nullable=False,
    )
