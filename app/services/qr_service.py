import qrcode
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..models import ShopOrder, Order
import os
from pathlib import Path


class QRService:
    """Сервис для работы с QR-кодами заказов"""
    
    # Длина токена для QR-кода (128 бит энтропии)
    TOKEN_LENGTH = 32
    
    # Алфавит для генерации токенов
    TOKEN_ALPHABET = string.ascii_letters + string.digits
    
    # Размер QR-кода
    QR_SIZE = 512
    
    # Папка для хранения QR-изображений
    QR_STORAGE_PATH = "app/static/qr"
    
    @classmethod
    def generate_token(cls) -> str:
        """Генерирует уникальный токен для QR-кода"""
        return ''.join(secrets.choice(cls.TOKEN_ALPHABET) for _ in range(cls.TOKEN_LENGTH))
    
    @classmethod
    def generate_qr_payload(cls, order) -> str:
        """Генерирует содержимое для QR-кода (публичный токен)"""
        # Используем формат /o/<token> для публичного доступа
        return f"/o/{order.qr_payload}"
    
    @classmethod
    def ensure_qr_storage_directory(cls) -> None:
        """Создает папку для хранения QR-изображений если её нет"""
        Path(cls.QR_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def generate_qr_image(cls, order) -> str:
        """Генерирует QR-изображение и возвращает путь к файлу"""
        if not order.qr_payload:
            raise ValueError("Order must have qr_payload before generating QR image")
        
        # Создаем папку если её нет
        cls.ensure_qr_storage_path()
        
        # Генерируем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Добавляем данные
        qr_data = cls.generate_qr_payload(order)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем файл
        filename = f"{order.id}.png"
        file_path = os.path.join(cls.QR_STORAGE_PATH, filename)
        img.save(file_path)
        
        # Возвращаем относительный путь для веб-доступа
        return f"qr/{filename}"
    
    @classmethod
    def ensure_qr_storage_path(cls) -> None:
        """Создает папку для хранения QR-изображений если её нет"""
        Path(cls.QR_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def generate_qr_for_order(cls, db: Session, order) -> bool:
        """Генерирует QR-код для заказа если его ещё нет"""
        try:
            # Если QR уже есть, не генерируем заново
            if order.has_qr:
                return True
            
            # Генерируем токен
            if not order.qr_payload:
                order.qr_payload = cls.generate_token()
            
            # Генерируем изображение
            order.qr_image_path = cls.generate_qr_image(order)
            order.qr_generated_at = datetime.now(timezone.utc)
            
            # Сохраняем в БД
            db.commit()
            db.refresh(order)
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error generating QR for order {order.id}: {e}")
            return False
    
    @classmethod
    def get_order_by_qr_token(cls, db: Session, token: str) -> Optional[Order]:
        """Получает заказ по QR-токену"""
        # Сначала ищем в основной таблице Order
        order = db.query(Order).filter(Order.qr_payload == token).first()
        if order:
            return order
        
        # Если не найден, ищем в ShopOrder (для совместимости)
        return db.query(ShopOrder).filter(ShopOrder.qr_payload == token).first()
    
    @classmethod
    def is_valid_qr_token(cls, token: str) -> bool:
        """Проверяет валидность QR-токена"""
        if not token or len(token) != cls.TOKEN_LENGTH:
            return False
        
        # Проверяем, что токен состоит только из допустимых символов
        return all(c in cls.TOKEN_ALPHABET for c in token)
    
    @classmethod
    def revoke_qr_token(cls, db: Session, order) -> bool:
        """Отзывает QR-токен заказа (при отмене)"""
        try:
            # Удаляем файл изображения если он есть
            if order.qr_image_path:
                file_path = os.path.join("app/static", order.qr_image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Очищаем поля QR
            order.qr_payload = None
            order.qr_image_path = None
            order.qr_generated_at = None
            
            db.commit()
            db.refresh(order)
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error revoking QR for order {order.id}: {e}")
            return False
    
    @classmethod
    def get_qr_image_url(cls, order) -> Optional[str]:
        """Возвращает URL для доступа к QR-изображению"""
        if not order.qr_image_path:
            return None
        
        return f"/static/{order.qr_image_path}"
    
    @classmethod
    def get_qr_public_url(cls, order) -> Optional[str]:
        """Возвращает публичный URL для доступа к заказу по QR"""
        if not order.qr_payload:
            return None
        
        return f"/o/{order.qr_payload}"
