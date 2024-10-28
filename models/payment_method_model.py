from db.session import Base
from db.base import ModelBase
from enum import Enum
from sqlalchemy import Column, String, Boolean, JSON, Enum as SQLEnum
from nanoid import generate


def generate_id():
    """Generates a random id"""
    id = f"pm_{str(generate())[:25]}"
    return id


def generate_id_account():
    """Generates a random id"""
    id = f"ca_{str(generate())[:25]}"
    return id


class PaymentMethodType(Enum):
    card = "card"
    token = "token"


class PaymentMethod(ModelBase, Base):
    __tablename__ = "payment_methods"
    id = Column(String(255), primary_key=True, nullable=True, default=generate_id)
    is_active = Column(Boolean, default=True)
    type = Column(
        SQLEnum(PaymentMethodType, name="payment_method_types"),
        nullable=False,
    )
    payment_method_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    developer_id = Column(String(255), nullable=False)
    app_id = Column(String(255), nullable=False)
    preferred = Column(Boolean, default=False)


class ConnectedAccount(ModelBase, Base):
    """Stores connected accounts"""

    __tablename__ = "connected_accounts"

    id = Column(String(255), primary_key=True, index=True, default=generate_id_account)
    account_id = Column(String(255), nullable=False)
    developer_id = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
