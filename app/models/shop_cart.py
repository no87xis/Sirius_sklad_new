from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class ShopCart(Base):
    __tablename__ = "shop_carts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)  # Уникальный ID сессии
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)  # Количество товара
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    product = relationship("Product")
    
    def __repr__(self):
        return f"<ShopCart(id={self.id}, session_id='{self.session_id}', product_id={self.product_id}, quantity={self.quantity})>"
