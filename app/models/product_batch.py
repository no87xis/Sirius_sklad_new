from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class ProductBatch(Base):
    """Партия товаров в пути или под заказ"""
    __tablename__ = "product_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Информация о партии
    batch_code = Column(String(50), unique=True, nullable=False, index=True)  # Уникальный код партии
    quantity = Column(Integer, nullable=False)  # Количество в партии
    expected_arrival_date = Column(DateTime(timezone=True), nullable=True)  # Ожидаемая дата прибытия
    
    # Цены
    purchase_price_rub = Column(Numeric(10, 2), nullable=True)  # Цена закупки
    preorder_price_rub = Column(Numeric(10, 2), nullable=True)  # Цена предзаказа (может быть ниже)
    final_price_rub = Column(Numeric(10, 2), nullable=True)  # Финальная цена после прибытия
    
    # Статус партии
    status = Column(String(50), nullable=False, default="in_transit", index=True)  # in_transit, arrived, cancelled
    notes = Column(Text, nullable=True)  # Заметки о партии
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    product = relationship("Product", back_populates="batches")
    
    def __repr__(self):
        return f"<ProductBatch(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, status={self.status})>"
    
    @property
    def is_available_for_preorder(self) -> bool:
        """Доступна ли партия для предзаказа"""
        return self.status == "in_transit" and self.preorder_price_rub is not None
    
    @property
    def is_arrived(self) -> bool:
        """Прибыла ли партия"""
        return self.status == "arrived"
    
    def mark_as_arrived(self, final_price: float = None):
        """Отмечает партию как прибывшую"""
        self.status = "arrived"
        if final_price is not None:
            self.final_price_rub = final_price
        self.updated_at = func.now()
    
    def get_current_price(self) -> float:
        """Получает текущую цену партии"""
        if self.is_arrived and self.final_price_rub:
            return float(self.final_price_rub)
        elif self.preorder_price_rub:
            return float(self.preorder_price_rub)
        else:
            return None
