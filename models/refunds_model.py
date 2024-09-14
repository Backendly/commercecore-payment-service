from db.base import Base, ModelBase
from sqlalchemy import Column, String, Boolean, JSON


class Refund(ModelBase, Base):
    __tablename__ = "refunds"
    refund_id = Column(String(255), primary_key=True, index=True)
    transaction_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    order_id = Column(String(255), nullable=False)
    app_id = Column(String(255), nullable=False)
    amount = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    reason = Column(String(255), nullable=True)
