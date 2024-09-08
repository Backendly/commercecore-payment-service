from ..db.session import Base
from ..db.base import ModelBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from datetime import datetime


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"

    is_active = Column(Boolean, default=True)
    method_type = Column(String, nullable=False)
    details = Column(
        JSON,
        nullable=False,
    )
