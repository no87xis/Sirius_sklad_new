from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Учётные поля
    quantity = Column(Integer, default=0, nullable=False)  # общий приход
    min_stock = Column(Integer, default=0, nullable=False)  # порог низкого остатка
    buy_price_eur = Column(Numeric(10, 2), nullable=True)  # входная цена (евро)
    sell_price_rub = Column(Numeric(10, 2), nullable=True)  # плановая розничная цена (руб)
    supplier_name = Column(String, nullable=True)  # поставщик
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    supplies = relationship("Supply", back_populates="product")
    orders = relationship("Order", back_populates="product")
