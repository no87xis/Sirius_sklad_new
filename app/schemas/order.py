from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.order import OrderStatus, PaymentMethod as PaymentMethodEnum

class OrderBase(BaseModel):
    phone: Optional[str] = Field(None, max_length=20)
    customer_name: Optional[str] = Field(None, max_length=200)
    client_city: Optional[str] = Field(None, max_length=100)
    product_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)
    unit_price_rub: Decimal = Field(..., ge=0)
    eur_rate: Decimal = Field(..., ge=0)
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.UNPAID)
    payment_note: Optional[str] = Field(None, max_length=120)
    # Новые поля для расширенной системы оплаты
    order_code: Optional[str] = Field(None, max_length=8, pattern=r'^[a-z]{3}\d{5}$')
    payment_method_id: Optional[int] = Field(None, gt=0)
    payment_instrument_id: Optional[int] = Field(None, gt=0)
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    paid_at: Optional[datetime] = None
    source: Optional[str] = Field(None, max_length=20)  # Источник заказа (manual/shop)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    phone: Optional[str] = Field(None, max_length=20)
    customer_name: Optional[str] = Field(None, max_length=200)
    client_city: Optional[str] = Field(None, max_length=100)
    product_id: Optional[int] = Field(None, gt=0)
    qty: Optional[int] = Field(None, gt=0)
    unit_price_rub: Optional[Decimal] = Field(None, ge=0)
    eur_rate: Optional[Decimal] = Field(None, ge=0)
    payment_method: Optional[PaymentMethodEnum] = None
    payment_note: Optional[str] = Field(None, max_length=120)
    status: Optional[OrderStatus] = None
    order_code: Optional[str] = Field(None, max_length=8, pattern=r'^[a-z]{3}\d{5}$')

class OrderResponse(OrderBase):
    id: int
    product_name: Optional[str] = None
    status: OrderStatus
    created_at: datetime
    issued_at: Optional[datetime] = None
    user_id: str
    total_amount: Decimal
    # Новые поля
    order_code: Optional[str] = None
    order_code_last4: Optional[str] = None
    payment_method_id: Optional[int] = None
    payment_instrument_id: Optional[int] = None
    paid_amount: Optional[Decimal] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
    pending_count: int
    issued_count: int
    denied_count: int

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
