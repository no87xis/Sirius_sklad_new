from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base


class ProductPhoto(Base):
    __tablename__ = "product_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)  # Имя файла на сервере
    original_filename = Column(String(255), nullable=False)  # Оригинальное имя файла
    file_path = Column(String(500), nullable=False)  # Путь к файлу
    file_size = Column(Integer, nullable=False)  # Размер файла в байтах
    mime_type = Column(String(100), nullable=False)  # MIME-тип файла
    is_main = Column(Boolean, default=False, nullable=False)  # Главное фото
    sort_order = Column(Integer, default=0, nullable=False)  # Порядок сортировки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    product = relationship("Product", back_populates="photos")
    
    def __repr__(self):
        return f"<ProductPhoto(id={self.id}, product_id={self.product_id}, filename='{self.filename}')>"
