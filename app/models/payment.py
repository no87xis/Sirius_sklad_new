from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class PaymentMethod(Base):
    """Методы оплаты (наличные, карта, USDT и т.д.)"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=True)  # cash, card, crypto, bank, other
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    instruments = relationship("PaymentInstrument", back_populates="method")
    cash_flows = relationship("CashFlow", back_populates="source_method")
    orders = relationship("Order", back_populates="payment_method_rel")


class PaymentInstrument(Base):
    """Инструменты оплаты (названия карт, кошельки и т.д.)"""
    __tablename__ = "payment_instruments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    method = relationship("PaymentMethod", back_populates="instruments")
    cash_flows = relationship("CashFlow", back_populates="source_instrument")
    orders = relationship("Order", back_populates="payment_instrument_rel")


class CashFlow(Base):
    """Движение денег (приход/расход)"""
    __tablename__ = "cash_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime(timezone=True), nullable=False)
    direction = Column(String(20), nullable=False)  # INFLOW/OUTFLOW
    source_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    source_instrument_id = Column(Integer, ForeignKey("payment_instruments.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    source_method = relationship("PaymentMethod", back_populates="cash_flows")
    source_instrument = relationship("PaymentInstrument", back_populates="cash_flows")
    order = relationship("Order", back_populates="cash_flows")
