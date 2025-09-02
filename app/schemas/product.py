from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from ..product_constants import ProductStatus, DEFAULT_STATUS


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    detailed_description: Optional[str] = Field(None, max_length=5000)
    min_stock: int = Field(0, ge=0)
    buy_price_eur: Optional[Decimal] = Field(None, ge=0)
    sell_price_rub: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = Field(None, max_length=200)


class ProductCreate(ProductBase):
    initial_quantity: int = Field(0, ge=0)
    availability_status: str = Field(DEFAULT_STATUS, max_length=20)
    expected_date: Optional[datetime] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    detailed_description: Optional[str] = Field(None, max_length=5000)
    min_stock: Optional[int] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    buy_price_eur: Optional[Decimal] = Field(None, ge=0)
    sell_price_rub: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = Field(None, max_length=200)
    availability_status: Optional[str] = Field(None, max_length=20)
    expected_date: Optional[datetime] = None


class ProductResponse(ProductBase):
    id: int
    quantity: int
    stock: int  # вычисляемое поле
    is_low_stock: bool  # вычисляемое поле
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
