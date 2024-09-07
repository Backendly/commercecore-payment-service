from ..db.session import Base
from ..db.base import ModelBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"

    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
