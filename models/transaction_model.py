from db.base import Base, ModelBase
from sqlalchemy import Column, String, ForeignKey


class Transaction(ModelBase, Base):
    __tablename__ = "transactions"
    transaction_id = Column(String(255), primary_key=True, index=True)
    order_id = Column(String(255), nullable=False)
    payment_method_id = Column(String(255), nullable=True)
    developer_id = Column(String(255), nullable=False)
    user_id = Column(String(225), nullable=False)
    amount = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
