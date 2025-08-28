from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from decimal import Decimal
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base
import enum


class OrderStatus(str, enum.Enum):
    PAID_NOT_ISSUED = "paid_not_issued"
    PAID_ISSUED = "paid_issued"
    PAID_DENIED = "paid_denied"


class PaymentMethod(str, enum.Enum):
    CARD = "card"
    CASH = "cash"
    UNPAID = "unpaid"
    OTHER = "other"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False, index=True)
    customer_name = Column(String, nullable=True)
    client_city = Column(String(100), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=True)  # денормализация для истории
    qty = Column(Integer, nullable=False)
    unit_price_rub = Column(Numeric(10, 2), nullable=False)
    eur_rate = Column(Numeric(10, 4), nullable=False, default=Decimal("0"))
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.UNPAID, nullable=False)
    payment_note = Column(String(120), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PAID_NOT_ISSUED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(String, ForeignKey("users.username"), nullable=False)
    
    # Связи
    product = relationship("Product", back_populates="orders")
    user = relationship("User", back_populates="orders")
