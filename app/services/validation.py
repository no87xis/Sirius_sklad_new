from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models import Product, User
import re

class ValidationService:
    """Сервис для валидации данных"""
    @staticmethod
    def validate_phone(phone: str) -> str:
        digits_only = ''.join(filter(str.isdigit, phone))
        if len(digits_only) < 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Номер телефона должен содержать минимум 10 цифр")
        if len(digits_only) == 11 and digits_only.startswith('8'):
            digits_only = '7' + digits_only[1:]
        return f"+7 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:9]}-{digits_only[9:]}"

    @staticmethod
    def validate_quantity(quantity: int, product_id: int, db: Session) -> int:
        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Количество должно быть больше 0")
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
        if quantity > product.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"На складе недостаточно товара. Доступно: {product.quantity}")
        return quantity

    @staticmethod
    def validate_price(price: float) -> float:
        if price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цена должна быть больше 0")
        return price

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Очищает HTML теги и потенциально опасный контент из текста"""
        # Удаляем все HTML теги
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Удаляем JavaScript код
        clean_text = re.sub(r'javascript:', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'alert\s*\([^)]*\)', '', clean_text)
        # Удаляем лишние пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
