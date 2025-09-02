from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from app.models.shop_order import ShopOrderStatus
from app.schemas.shop_cart import ShopCartItemResponse
from app.constants.delivery import DeliveryOption


class ShopOrderBase(BaseModel):
    customer_name: str = Field(..., max_length=200)
    customer_phone: str = Field(..., max_length=20)
    customer_city: Optional[str] = Field(None, max_length=100)
    payment_method_id: Optional[int] = Field(None, gt=0)
    # Поля доставки
    delivery_option: DeliveryOption = Field(..., description="Вариант доставки")
    delivery_city_other: Optional[str] = Field(None, max_length=100, description="Город для 'Другая (по согласованию)'")


class ShopOrderCreate(ShopOrderBase):
    """Создание заказа из корзины"""
    cart_items: List[ShopCartItemResponse] = Field(..., description="Список товаров из корзины")
    
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class ShopOrderResponse(ShopOrderBase):
    id: int
    order_code: str
    order_code_last4: str
    product_id: int
    product_name: str
    quantity: int
    unit_price_rub: Decimal
    total_amount: Decimal
    payment_method_name: Optional[str]
    status: ShopOrderStatus
    reserved_until: datetime
    expected_delivery_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]
    completed_at: Optional[datetime]
    # Поля доставки
    delivery_cost_rub: Optional[int] = Field(None, description="Стоимость доставки")
    delivery_display_name: Optional[str] = Field(None, description="Отображаемое название доставки")
    total_with_delivery: Optional[Decimal] = Field(None, description="Общая стоимость с доставкой")
    
    class Config:
        from_attributes = True


class ShopOrderUpdate(BaseModel):
    """Обновление заказа менеджером"""
    status: Optional[ShopOrderStatus] = None
    payment_method_id: Optional[int] = Field(None, gt=0)
    expected_delivery_date: Optional[date] = None
    # Поля доставки
    delivery_option: Optional[DeliveryOption] = None
    delivery_city_other: Optional[str] = Field(None, max_length=100)
    delivery_cost_rub: Optional[int] = None


class ShopOrderSearch(BaseModel):
    """Поиск заказа клиентом"""
    order_code: str = Field(..., max_length=8)
    customer_phone: str = Field(..., max_length=20)


class ShopOrderListResponse(BaseModel):
    """Список заказов для аналитики"""
    orders: List[ShopOrderResponse]
    total: int
    total_amount: Decimal
    status_counts: dict[str, int]
    
    class Config:
        from_attributes = True


class ShopOrderAnalytics(BaseModel):
    """Аналитика по заказам"""
    total_orders: int
    total_amount: Decimal
    paid_not_delivered: int
    paid_not_delivered_amount: Decimal
    paid_and_delivered: int
    paid_and_delivered_amount: Decimal
    ordered_not_paid: int
    ordered_not_paid_amount: Decimal
    reserved_not_paid: int
    reserved_not_paid_amount: Decimal
    
    class Config:
        from_attributes = True
