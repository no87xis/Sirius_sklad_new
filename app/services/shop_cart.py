from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from app.models import ShopCart, Product, ProductPhoto
from app.schemas.shop_cart import ShopCartCreate, ShopCartUpdate, ShopCartSummary, ShopCartItemResponse


class ShopCartService:
    """Сервис для работы с корзиной магазина"""
    
    @staticmethod
    def add_to_cart(db: Session, cart_data: ShopCartCreate) -> ShopCart:
        """Добавляет товар в корзину"""
        # Проверяем, есть ли уже такой товар в корзине
        existing_item = db.query(ShopCart).filter(
            and_(
                ShopCart.session_id == cart_data.session_id,
                ShopCart.product_id == cart_data.product_id
            )
        ).first()
        
        if existing_item:
            # Обновляем количество
            existing_item.quantity += cart_data.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Создаём новый элемент корзины
            cart_item = ShopCart(
                session_id=cart_data.session_id,
                product_id=cart_data.product_id,
                quantity=cart_data.quantity
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def update_cart_item(db: Session, session_id: str, product_id: int, quantity: int) -> Optional[ShopCart]:
        """Обновляет количество товара в корзине"""
        cart_item = db.query(ShopCart).filter(
            and_(
                ShopCart.session_id == session_id,
                ShopCart.product_id == product_id
            )
        ).first()
        
        if not cart_item:
            return None
        
        if quantity <= 0:
            # Удаляем товар из корзины
            db.delete(cart_item)
            db.commit()
            return None
        
        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item
    
    @staticmethod
    def remove_from_cart(db: Session, session_id: str, product_id: int) -> bool:
        """Удаляет товар из корзины"""
        cart_item = db.query(ShopCart).filter(
            and_(
                ShopCart.session_id == session_id,
                ShopCart.product_id == product_id
            )
        ).first()
        
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True
    
    @staticmethod
    def clear_cart(db: Session, session_id: str) -> bool:
        """Очищает корзину"""
        deleted_count = db.query(ShopCart).filter(
            ShopCart.session_id == session_id
        ).delete()
        
        db.commit()
        return deleted_count > 0
    
    @staticmethod
    def get_cart_items(db: Session, session_id: str) -> List[ShopCartItemResponse]:
        """Получает все товары в корзине с расширенной информацией"""
        cart_items = db.query(ShopCart).filter(
            ShopCart.session_id == session_id
        ).all()
        
        result = []
        for cart_item in cart_items:
            # Получаем информацию о товаре
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if not product:
                continue
            
            # Получаем главное фото
            main_photo = db.query(ProductPhoto).filter(
                and_(
                    ProductPhoto.product_id == product.id,
                    ProductPhoto.is_main == True
                )
            ).first()
            
            # Вычисляем доступный остаток (исключая резервы)
            available_stock = product.quantity
            
            # Вычисляем общую стоимость
            unit_price = product.sell_price_rub or Decimal('0')
            total_price = unit_price * cart_item.quantity
            
            # Формируем URL для фото
            main_photo_url = None
            if main_photo and main_photo.file_path:
                # Убираем 'app/static/' из пути если есть
                photo_path = main_photo.file_path.replace('app/static/', '')
                main_photo_url = f"/static/{photo_path}"
            
            cart_item_response = ShopCartItemResponse(
                id=cart_item.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                session_id=cart_item.session_id,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at,
                product_name=product.name,
                product_code=getattr(product, 'product_code', None),
                unit_price_rub=unit_price,
                total_price=total_price,
                available_stock=available_stock,
                main_photo_url=main_photo_url
            )
            
            result.append(cart_item_response)
        
        return result
    
    @staticmethod
    def get_cart_summary(db: Session, session_id: str) -> ShopCartSummary:
        """Получает сводку по корзине"""
        cart_items = ShopCartService.get_cart_items(db, session_id)
        
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.total_price for item in cart_items if item.total_price)
        
        return ShopCartSummary(
            items=cart_items,
            total_items=total_items,
            total_amount=total_amount
        )
    
    @staticmethod
    def get_cart_count(db: Session, session_id: str) -> int:
        """Получает количество товаров в корзине"""
        return db.query(ShopCart).filter(
            ShopCart.session_id == session_id
        ).count()
    
    @staticmethod
    def validate_cart(db: Session, session_id: str) -> List[str]:
        """Проверяет валидность корзины и возвращает список ошибок"""
        errors = []
        cart_items = db.query(ShopCart).filter(
            ShopCart.session_id == session_id
        ).all()
        
        for cart_item in cart_items:
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if not product:
                errors.append(f"Товар с ID {cart_item.product_id} не найден")
                continue
            
            if cart_item.quantity <= 0:
                errors.append(f"Некорректное количество для товара '{product.name}'")
                continue
            
            # Проверяем остаток
            if product.quantity < cart_item.quantity:
                errors.append(f"Недостаточно товара '{product.name}'. Доступно: {product.quantity}")
        
        return errors
