from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from ..models.product_batch import ProductBatch
from ..models.product import Product


class DeliveryNotificationService:
    """Сервис для уведомлений о приближающейся доставке"""
    
    @staticmethod
    def get_upcoming_deliveries(db: Session, days_ahead: int = 5) -> List[dict]:
        """Получает товары с приближающейся датой доставки"""
        today = datetime.now().date()
        target_date = today + timedelta(days=days_ahead)
        
        # Получаем партии товаров с приближающейся датой доставки
        upcoming_batches = db.query(ProductBatch).filter(
            and_(
                ProductBatch.expected_arrival_date.isnot(None),
                ProductBatch.expected_arrival_date <= target_date,
                ProductBatch.expected_arrival_date >= today,
                ProductBatch.status == "in_transit"
            )
        ).all()
        
        notifications = []
        for batch in upcoming_batches:
            days_until_delivery = (batch.expected_arrival_date.date() - today).days
            
            # Получаем информацию о товаре
            product = db.query(Product).filter(Product.id == batch.product_id).first()
            if not product:
                continue
            
            notification = {
                "batch_id": batch.id,
                "product_id": batch.product_id,
                "product_name": product.name,
                "batch_code": batch.batch_code,
                "quantity": batch.quantity,
                "expected_arrival_date": batch.expected_arrival_date,
                "days_until_delivery": days_until_delivery,
                "is_urgent": days_until_delivery <= 1,  # Срочно если завтра или сегодня
                "preorder_price": batch.preorder_price_rub,
                "notes": batch.notes
            }
            notifications.append(notification)
        
        # Сортируем по дате доставки
        notifications.sort(key=lambda x: x["expected_arrival_date"])
        return notifications
    
    @staticmethod
    def get_overdue_deliveries(db: Session) -> List[dict]:
        """Получает товары с просроченной датой доставки"""
        today = datetime.now().date()
        
        # Получаем партии товаров с просроченной датой доставки
        overdue_batches = db.query(ProductBatch).filter(
            and_(
                ProductBatch.expected_arrival_date.isnot(None),
                ProductBatch.expected_arrival_date < today,
                ProductBatch.status == "in_transit"
            )
        ).all()
        
        notifications = []
        for batch in overdue_batches:
            days_overdue = (today - batch.expected_arrival_date.date()).days
            
            # Получаем информацию о товаре
            product = db.query(Product).filter(Product.id == batch.product_id).first()
            if not product:
                continue
            
            notification = {
                "batch_id": batch.id,
                "product_id": batch.product_id,
                "product_name": product.name,
                "batch_code": batch.batch_code,
                "quantity": batch.quantity,
                "expected_arrival_date": batch.expected_arrival_date,
                "days_overdue": days_overdue,
                "is_overdue": True,
                "preorder_price": batch.preorder_price_rub,
                "notes": batch.notes
            }
            notifications.append(notification)
        
        # Сортируем по количеству дней просрочки
        notifications.sort(key=lambda x: x["days_overdue"], reverse=True)
        return notifications
    
    @staticmethod
    def mark_batch_as_arrived(db: Session, batch_id: int, final_price: Optional[float] = None) -> bool:
        """Отмечает партию как прибывшую"""
        batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
        if not batch:
            return False
        
        batch.mark_as_arrived(final_price)
        db.commit()
        return True
    
    @staticmethod
    def update_delivery_date(db: Session, batch_id: int, new_date: datetime) -> bool:
        """Обновляет дату доставки"""
        batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
        if not batch:
            return False
        
        batch.expected_arrival_date = new_date
        batch.updated_at = datetime.now()
        db.commit()
        return True
