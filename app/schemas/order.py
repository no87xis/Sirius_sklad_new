from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.order import OrderStatus

class OrderBase(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    customer_name: Optional[str] = Field(None, max_length=200)
    product_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)
    unit_price_rub: Decimal = Field(..., ge=0)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    customer_name: Optional[str] = Field(None, max_length=200)
    qty: Optional[int] = Field(None, gt=0)
    unit_price_rub: Optional[Decimal] = Field(None, ge=0)
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase):
    id: int
    product_name: Optional[str] = None
    status: OrderStatus
    created_at: datetime
    issued_at: Optional[datetime] = None
    user_id: str
    total_amount: Decimal

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
