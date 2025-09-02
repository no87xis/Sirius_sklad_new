from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Date
from decimal import Decimal
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base
from ..constants.delivery import DeliveryOption
import enum


class OrderStatus(str, enum.Enum):
    # Основные статусы
    IN_TRANSIT = "in_transit"           # В пути
    ON_ORDER = "on_order"               # Под заказ
    UNPAID = "unpaid"                   # Не оплачен
    PAID_NOT_ISSUED = "paid_not_issued" # Оплачен, не выдан
    PAID_ISSUED = "paid_issued"         # Оплачен и выдан
    PAID_DENIED = "paid_denied"         # Оплачен, но отказано в выдаче
    
    # Статусы доставки
    COURIER_GROZNY = "courier_grozny"   # Курьеру в Грозный
    COURIER_MAK = "courier_mak"         # Курьеру в Махачкалу
    COURIER_KHAS = "courier_khas"       # Курьеру в Хасавюрт
    COURIER_OTHER = "courier_other"     # Курьеру в другой город
    SELF_PICKUP = "self_pickup"         # Ожидает выдачи (самовывоз)
    OTHER = "other"                     # Прочие


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
    
    # Новые поля для расширенной системы оплаты
    order_code = Column(String(8), unique=True, nullable=True, index=True)
    order_code_last4 = Column(String(4), nullable=True, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True, index=True)
    payment_instrument_id = Column(Integer, ForeignKey("payment_instruments.id"), nullable=True, index=True)
    paid_amount = Column(Numeric(10, 2), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Старые поля (оставляем для совместимости)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.UNPAID, nullable=False)
    payment_note = Column(String(120), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PAID_NOT_ISSUED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(String, ForeignKey("users.username"), nullable=False)
    
    # Источник заказа (manual - ручной, shop - из магазина)
    source = Column(String(20), nullable=True, default="manual")
    
    # QR-код поля
    qr_payload = Column(String, nullable=True, index=True)  # Уникальный токен для QR-кода
    qr_image_path = Column(String, nullable=True)  # Путь к изображению QR-кода
    qr_generated_at = Column(DateTime(timezone=True), nullable=True)  # Когда сгенерирован QR-код
    
    # Поля системы доставки
    delivery_option = Column(String(50), nullable=True, index=True)  # Тип доставки
    delivery_city_other = Column(String(100), nullable=True)  # Город для "Другая (по согласованию)"
    delivery_unit_price_rub = Column(Integer, nullable=True, default=300)  # Тариф за единицу
    delivery_units = Column(Integer, nullable=True)  # Количество единиц для расчета
    delivery_cost_rub = Column(Integer, nullable=True)  # Итоговая стоимость доставки
    delivery_payment_enabled = Column(String(5), nullable=True, default="FALSE")  # Оплата доставки включена
    
    # Связи
    product = relationship("Product", back_populates="orders")
    user = relationship("User", back_populates="orders")
    
    # Новые связи
    payment_method_rel = relationship("PaymentMethod", back_populates="orders")
    payment_instrument_rel = relationship("PaymentInstrument", back_populates="orders")
    cash_flows = relationship("CashFlow", back_populates="order")
    
    @property
    def has_qr(self) -> bool:
        """Проверяет, есть ли QR-код у заказа"""
        return bool(self.qr_payload and self.qr_image_path)
    
    @property
    def delivery_display_name(self) -> str:
        """Получает отображаемое название варианта доставки"""
        from ..constants.delivery import get_delivery_display_name
        if self.delivery_option:
            return get_delivery_display_name(self.delivery_option)
        return "Не указано"
    
    @property
    def total_with_delivery(self) -> Decimal:
        """Получает общую стоимость заказа с доставкой"""
        total = self.qty * self.unit_price_rub
        if self.delivery_cost_rub:
            total += Decimal(str(self.delivery_cost_rub))
        return total
    
    @property
    def auto_status(self) -> str:
        """Автоматически определяет статус заказа на основе данных"""
        from ..models.product import Product
        
        # Проверяем наличие товара
        if hasattr(self, 'product') and self.product:
            product = self.product
        else:
            # Если связь не загружена, получаем продукт из БД
            from ..db import get_db
            db = next(get_db())
            product = db.query(Product).filter(Product.id == self.product_id).first()
        
        if not product:
            return OrderStatus.OTHER
        
        # Определяем статус на основе наличия товара
        if product.availability_status == 'IN_TRANSIT':
            return OrderStatus.IN_TRANSIT
        elif product.availability_status == 'ON_ORDER':
            return OrderStatus.ON_ORDER
        elif product.availability_status == 'IN_STOCK' and product.quantity > 0:
            # Товар в наличии
            if self.paid_amount and self.paid_amount > 0:
                # Товар оплачен
                if self.delivery_option and self.delivery_option.startswith('COURIER_'):
                    # Курьерская доставка
                    if self.delivery_option == 'COURIER_GROZNY':
                        return OrderStatus.COURIER_GROZNY
                    elif self.delivery_option == 'COURIER_MAK':
                        return OrderStatus.COURIER_MAK
                    elif self.delivery_option == 'COURIER_KHAS':
                        return OrderStatus.COURIER_KHAS
                    elif self.delivery_option == 'COURIER_OTHER':
                        return OrderStatus.COURIER_OTHER
                    else:
                        return OrderStatus.COURIER_GROZNY  # По умолчанию
                else:
                    # Самовывоз
                    return OrderStatus.SELF_PICKUP
            else:
                # Товар не оплачен
                return OrderStatus.UNPAID
        else:
            # Товар отсутствует
            return OrderStatus.OTHER
