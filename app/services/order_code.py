import random
import string
from sqlalchemy.orm import Session
from app.models import Order


class OrderCodeService:
    """Сервис для работы с кодами заказов"""
    
    @staticmethod
    def generate_order_code() -> str:
        """Генерирует уникальный код заказа: 3 буквы + 5 цифр"""
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        digits = ''.join(random.choices(string.digits, k=5))
        return letters + digits
    
    @staticmethod
    def generate_unique_order_code(db: Session, max_attempts: int = 10) -> str:
        """Генерирует уникальный код заказа с проверкой в базе данных"""
        for _ in range(max_attempts):
            code = OrderCodeService.generate_order_code()
            # Проверяем уникальность
            existing = db.query(Order).filter(Order.order_code == code).first()
            if not existing:
                return code
        
        # Если не удалось сгенерировать за max_attempts, добавляем случайный суффикс
        base_code = OrderCodeService.generate_order_code()
        suffix = ''.join(random.choices(string.digits, k=2))
        return base_code[:6] + suffix
    
    @staticmethod
    def get_last4_from_code(order_code: str) -> str:
        """Извлекает последние 4 символа из кода заказа"""
        return order_code[-4:] if order_code and len(order_code) >= 4 else ""
    
    @staticmethod
    def search_by_code(db: Session, search_term: str) -> list[Order]:
        """Поиск заказов по коду (полному или последним 4 символам)"""
        if len(search_term) == 4:
            # Поиск по последним 4 символам
            return db.query(Order).filter(Order.order_code_last4 == search_term.upper()).all()
        else:
            # Поиск по полному коду
            return db.query(Order).filter(Order.order_code == search_term.upper()).all()
    
    @staticmethod
    def search_by_code_or_phone(db: Session, search_term: str) -> list[Order]:
        """Поиск заказов по коду или телефону"""
        # Сначала пробуем поиск по коду
        orders_by_code = OrderCodeService.search_by_code(db, search_term)
        if orders_by_code:
            return orders_by_code
        
        # Если по коду не найдено, ищем по телефону
        return db.query(Order).filter(Order.phone.contains(search_term)).all()
