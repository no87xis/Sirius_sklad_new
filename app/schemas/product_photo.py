from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductPhotoBase(BaseModel):
    product_id: int = Field(..., gt=0)
    filename: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_path: str = Field(..., max_length=500)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., max_length=100)
    is_main: bool = Field(default=False)
    sort_order: int = Field(default=0, ge=0)


class ProductPhotoCreate(ProductPhotoBase):
    pass


class ProductPhotoUpdate(BaseModel):
    filename: Optional[str] = Field(None, max_length=255)
    original_filename: Optional[str] = Field(None, max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, gt=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    is_main: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ProductPhotoResponse(ProductPhotoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductPhotoUpload(BaseModel):
    """Схема для загрузки фото"""
    product_id: int = Field(..., gt=0)
    is_main: bool = Field(default=False)
    sort_order: int = Field(default=0, ge=0)
