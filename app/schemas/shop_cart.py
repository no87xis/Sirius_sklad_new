from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ShopCartBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class ShopCartCreate(ShopCartBase):
    session_id: str = Field(..., max_length=255)


class ShopCartUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class ShopCartResponse(ShopCartBase):
    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShopCartItemResponse(ShopCartResponse):
    """Расширенная схема корзины с информацией о товаре"""
    product_name: str
    product_code: Optional[str]
    unit_price_rub: Optional[Decimal]
    total_price: Optional[Decimal]
    available_stock: int
    main_photo_url: Optional[str] = None
    stock_status: str  # Статус товара: "В наличии", "Под заказ", "В пути"
    
    class Config:
        from_attributes = True


class ShopCartSummary(BaseModel):
    """Сводка по корзине"""
    items: List[ShopCartItemResponse]
    total_items: int
    total_amount: Decimal
    
    class Config:
        from_attributes = True
