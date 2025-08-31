from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.models import ShopOrder, ShopOrderStatus, Product, PaymentMethodModel
from app.schemas.shop_order import ShopOrderCreate, ShopOrderUpdate, ShopOrderSearch, ShopOrderAnalytics
from app.services.order_code import OrderCodeService
from app.services.qr_service import QRService


class ShopOrderService:
    """Сервис для работы с заказами магазина"""
    
    @staticmethod
    def create_orders_from_cart(db: Session, order_data: ShopOrderCreate) -> List[ShopOrder]:
        """Создаёт заказы из корзины (отдельный заказ для каждого товара)"""
        orders = []
        
        for cart_item in order_data.cart_items:
            # Получаем информацию о товару
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if not product:
                continue
            
            # Генерируем уникальный код заказа
            order_code = OrderCodeService.generate_unique_order_code(db)
            order_code_last4 = OrderCodeService.get_last4_from_code(order_code)
            
            # Вычисляем стоимость заказа
            unit_price = product.sell_price_rub or Decimal('0')
            total_amount = unit_price * cart_item.quantity
            
            # Получаем название способа оплаты
            payment_method_name = None
            if order_data.payment_method_id:
                payment_method = db.query(PaymentMethodModel).filter(
                    PaymentMethodModel.id == order_data.payment_method_id
                ).first()
                if payment_method:
                    payment_method_name = payment_method.name
            
            # Создаём заказ
            order = ShopOrder(
                order_code=order_code,
                order_code_last4=order_code_last4,
                customer_name=order_data.customer_name,
                customer_phone=order_data.customer_phone,
                customer_city=order_data.customer_city,
                product_id=product.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                unit_price_rub=unit_price,
                total_amount=total_amount,
                payment_method_id=order_data.payment_method_id,
                payment_method_name=payment_method_name,
                status=ShopOrderStatus.ORDERED_NOT_PAID,
                reserved_until=None,
                expected_delivery_date=product.expected_date
            )
            
            db.add(order)
            orders.append(order)
        
        db.commit()
        
        # Обновляем объекты после коммита
        for order in orders:
            db.refresh(order)
        
        # Генерируем QR-коды для всех заказов
        for order in orders:
            QRService.generate_qr_for_order(db, order)
        
        return orders
    
    @staticmethod
    def get_order_by_code_and_phone(db: Session, order_code: str, customer_phone: str) -> Optional[ShopOrder]:
        """Получает заказ по коду и телефону клиента"""
        return db.query(ShopOrder).filter(
            and_(
                ShopOrder.order_code == order_code,
                ShopOrder.customer_phone == customer_phone
            )
        ).first()
    
    @staticmethod
    def search_orders(db: Session, search_data: ShopOrderSearch) -> List[ShopOrder]:
        """Поиск заказов по коду и телефону"""
        # Сначала пробуем поиск по полному коду
        orders = db.query(ShopOrder).filter(
            and_(
                ShopOrder.order_code == search_data.order_code,
                ShopOrder.customer_phone == search_data.customer_phone
            )
        ).all()
        
        if orders:
            return orders
        
        # Если не найдено, пробуем поиск по последним 4 символам
        if len(search_data.order_code) == 4:
            orders = db.query(ShopOrder).filter(
                and_(
                    ShopOrder.order_code_last4 == search_data.order_code,
                    ShopOrder.customer_phone == search_data.customer_phone
                )
            ).all()
            return orders
        
        return []
    
    @staticmethod
    def update_order(db: Session, order_id: int, update_data: ShopOrderUpdate) -> Optional[ShopOrder]:
        """Обновляет заказ (для менеджера)"""
        order = db.query(ShopOrder).filter(ShopOrder.id == order_id).first()
        if not order:
            return None
        
        # Обновляем статус
        if update_data.status:
            old_status = order.status
            order.status = update_data.status
            
            # Устанавливаем даты в зависимости от статуса
            if update_data.status == ShopOrderStatus.PAID and old_status != ShopOrderStatus.PAID:
                order.paid_at = datetime.now(timezone.utc)
            elif update_data.status == ShopOrderStatus.COMPLETED and old_status != ShopOrderStatus.COMPLETED:
                order.completed_at = datetime.now(timezone.utc)
        
        # Обновляем способ оплаты
        if update_data.payment_method_id:
            payment_method = db.query(PaymentMethodModel).filter(
                PaymentMethodModel.id == update_data.payment_method_id
            ).first()
            if payment_method:
                order.payment_method_id = update_data.payment_method_id
                order.payment_method_name = payment_method.name
        
        # Обновляем ожидаемую дату доставки
        if update_data.expected_delivery_date:
            order.expected_delivery_date = update_data.expected_delivery_date
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_expired_orders(db: Session) -> List[ShopOrder]:
        """Получает заказы с истёкшим резервом"""
        now = datetime.now(timezone.utc)
        return db.query(ShopOrder).filter(
            and_(
                ShopOrder.status == ShopOrderStatus.RESERVED,
                ShopOrder.reserved_until < now
            )
        ).all()
    
    @staticmethod
    def expire_reserved_orders(db: Session) -> int:
        """Снимает резерв с истёкших заказов"""
        expired_orders = ShopOrderService.get_expired_orders(db)
        
        for order in expired_orders:
            order.status = ShopOrderStatus.EXPIRED
        
        db.commit()
        return len(expired_orders)
    
    @staticmethod
    def get_orders_for_analytics(db: Session, start_date: Optional[datetime] = None, 
                                end_date: Optional[datetime] = None, 
                                payment_method_id: Optional[int] = None) -> List[ShopOrder]:
        """Получает заказы для аналитики с фильтрами"""
        query = db.query(ShopOrder)
        
        if start_date:
            query = query.filter(ShopOrder.created_at >= start_date)
        if end_date:
            query = query.filter(ShopOrder.created_at <= end_date)
        if payment_method_id:
            query = query.filter(ShopOrder.payment_method_id == payment_method_id)
        
        return query.order_by(ShopOrder.created_at.desc()).all()
    
    @staticmethod
    def get_analytics(db: Session, start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None) -> ShopOrderAnalytics:
        """Получает аналитику по заказам"""
        orders = ShopOrderService.get_orders_for_analytics(db, start_date, end_date)
        
        total_orders = len(orders)
        total_amount = sum(order.total_amount for order in orders)
        
        # Оплачено, но не выдано
        paid_not_delivered = [o for o in orders if o.status == ShopOrderStatus.PAID]
        paid_not_delivered_amount = sum(o.total_amount for o in paid_not_delivered)
        
        # Оплачено и выдано
        paid_and_delivered = [o for o in orders if o.status == ShopOrderStatus.COMPLETED]
        paid_and_delivered_amount = sum(o.total_amount for o in paid_and_delivered)
        
        # Не оплачено (оформлено, но не оплачено)
        ordered_not_paid = [o for o in orders if o.status == ShopOrderStatus.ORDERED_NOT_PAID]
        ordered_not_paid_amount = sum(o.total_amount for o in ordered_not_paid)
        
        # Зарезервировано (оплачено, но не выдано)
        reserved_not_paid = [o for o in orders if o.status == ShopOrderStatus.RESERVED]
        reserved_not_paid_amount = sum(o.total_amount for o in reserved_not_paid)
        
        return ShopOrderAnalytics(
            total_orders=total_orders,
            total_amount=total_amount,
            paid_not_delivered=len(paid_not_delivered),
            paid_not_delivered_amount=paid_not_delivered_amount,
            paid_and_delivered=len(paid_and_delivered),
            paid_and_delivered_amount=paid_and_delivered_amount,
            ordered_not_paid=len(ordered_not_paid),
            ordered_not_paid_amount=ordered_not_paid_amount,
            reserved_not_paid=len(reserved_not_paid),
            reserved_not_paid_amount=reserved_not_paid_amount
        )
    
    @staticmethod
    def get_orders_by_status(db: Session, status: ShopOrderStatus, 
                           limit: int = 100) -> List[ShopOrder]:
        """Получает заказы по статусу"""
        return db.query(ShopOrder).filter(
            ShopOrder.status == status
        ).order_by(ShopOrder.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_orders(db: Session, limit: int = 50) -> List[ShopOrder]:
        """Получает последние заказы"""
        return db.query(ShopOrder).order_by(
            ShopOrder.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def reserve_product_on_payment(db: Session, order_id: int) -> bool:
        """Резервирует товар при оплате заказа"""
        order = db.query(ShopOrder).filter(ShopOrder.id == order_id).first()
        if not order:
            return False
        
        # Проверяем, что заказ в статусе "Оформлен, не оплачен"
        if order.status != ShopOrderStatus.ORDERED_NOT_PAID:
            return False
        
        # Получаем товар
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if not product:
            return False
        
        # Проверяем достаточность остатков
        from ..services.products import calculate_stock
        current_stock = calculate_stock(product, db)
        if current_stock < order.quantity:
            return False
        
        # Резервируем товар на 48 часов
        order.reserved_until = datetime.now(timezone.utc) + timedelta(hours=48)
        order.status = ShopOrderStatus.RESERVED
        
        db.commit()
        db.refresh(order)
        
        return True
