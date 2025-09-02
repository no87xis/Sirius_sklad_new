from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base
from ..product_constants import ProductStatus, DEFAULT_STATUS


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    detailed_description = Column(Text, nullable=True)  # Подробное описание для магазина
    
    # Учётные поля
    quantity = Column(Integer, default=0, nullable=False)  # общий приход
    min_stock = Column(Integer, default=0, nullable=False)  # порог низкого остатка
    buy_price_eur = Column(Numeric(10, 2), nullable=True)  # входная цена (евро)
    sell_price_rub = Column(Numeric(10, 2), nullable=True)  # плановая розничная цена (руб)
    supplier_name = Column(String, nullable=True)  # поставщик
    
    # Новые поля для статуса товара
    availability_status = Column(String(20), default=DEFAULT_STATUS, nullable=False, index=True)
    expected_date = Column(Date, nullable=True)  # дата ожидаемого поступления
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    supplies = relationship("Supply", back_populates="product")
    orders = relationship("Order", back_populates="product")
    photos = relationship("ProductPhoto", back_populates="product", cascade="all, delete-orphan")
    batches = relationship("ProductBatch", back_populates="product", cascade="all, delete-orphan")
    
    @property
    def main_photo(self):
        """Возвращает главное фото товара"""
        for photo in self.photos:
            if photo.is_main:
                return photo
        return self.photos[0] if self.photos else None
    
    @property
    def available_photos(self):
        """Возвращает все доступные фото товара, отсортированные по порядку"""
        return sorted(self.photos, key=lambda x: (x.sort_order, x.created_at))
    
    @property
    def stock_status(self):
        """Возвращает статус наличия товара"""
        if self.quantity > 0:
            return "В наличии"
        elif self.expected_date:
            return f"Под заказ (ожидается {self.expected_date.strftime('%d.%m.%Y')})"
        else:
            return "Под заказ"
    
    @property
    def active_batches(self):
        """Возвращает активные партии товара"""
        return [batch for batch in self.batches if batch.status in ["in_transit", "arrived"]]
    
    @property
    def preorder_price(self):
        """Возвращает цену предзаказа (самую низкую из доступных партий)"""
        available_batches = [batch for batch in self.batches if batch.is_available_for_preorder]
        if available_batches:
            return min(batch.preorder_price_rub for batch in available_batches if batch.preorder_price_rub)
        return None
    
    @property
    def total_in_transit(self):
        """Возвращает общее количество товара в пути"""
        return sum(batch.quantity for batch in self.batches if batch.status == "in_transit")
    
    @property
    def total_on_order(self):
        """Возвращает общее количество товара под заказ"""
        return sum(batch.quantity for batch in self.batches if batch.status == "in_transit" and batch.preorder_price_rub)
