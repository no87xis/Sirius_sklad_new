from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class SupplyBase(BaseModel):
    product_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)
    supplier_name: str = Field(..., min_length=1, max_length=200)
    buy_price_eur: Decimal = Field(..., ge=0)


class SupplyCreate(SupplyBase):
    pass


class SupplyResponse(SupplyBase):
    id: int
    created_at: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class SupplyListResponse(BaseModel):
    supplies: list[SupplyResponse]
    total: int
