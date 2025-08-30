from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base
from enum import Enum


class ShopOrderStatus(str, Enum):
    """Статусы заказов магазина"""
    RESERVED = "reserved"  # Зарезервирован (2 суток)
    PAID = "paid"  # Оплачен
    AWAITING_DELIVERY = "awaiting_delivery"  # Ждём поступления
    READY_FOR_PICKUP = "ready_for_pickup"  # Готов к выдаче
    COMPLETED = "completed"  # Выдан
    EXPIRED = "expired"  # Истёк резерв
    CANCELLED = "cancelled"  # Отменён
    ORDERED_NOT_PAID = "ordered_not_paid"  # Заказан, но не оплачен


class ShopOrder(Base):
    __tablename__ = "shop_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(8), unique=True, nullable=False, index=True)  # Уникальный код заказа
    order_code_last4 = Column(String(4), nullable=False, index=True)  # Последние 4 символа для поиска
    
    # Информация о клиенте
    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_city = Column(String(100), nullable=True)
    
    # Информация о товаре
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_rub = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Способ оплаты
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    payment_method_name = Column(String(100), nullable=True)
    
    # Статус и резервирование
    status = Column(String(20), default=ShopOrderStatus.ORDERED_NOT_PAID, nullable=False, index=True)
    reserved_until = Column(DateTime(timezone=True), nullable=True)  # До какого времени зарезервирован (может быть NULL)
    expected_delivery_date = Column(Date, nullable=True)  # Ожидаемая дата поступления
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    product = relationship("Product")
    payment_method = relationship("PaymentMethod")
    
    def __repr__(self):
        return f"<ShopOrder(id={self.id}, order_code='{self.order_code}', status='{self.status}')>"
    
    @property
    def is_expired(self) -> bool:
        """Проверяет, истёк ли резерв"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.reserved_until
    
    @property
    def is_reserved(self) -> bool:
        """Проверяет, активен ли резерв"""
        return self.status == ShopOrderStatus.RESERVED and not self.is_expired
