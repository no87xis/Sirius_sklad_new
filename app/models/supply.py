from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class Supply(Base):
    __tablename__ = "supplies"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)  # количество
    supplier_name = Column(String, nullable=False)
    buy_price_eur = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    product = relationship("Product", back_populates="supplies")
