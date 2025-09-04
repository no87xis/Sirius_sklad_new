from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from ..models import Order, Product, OrderStatus, PaymentMethodEnum
from ..schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate
from ..services.products import calculate_stock
from fastapi import HTTPException, status


class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_orders(self, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[Order]:
        """Получить список заказов с фильтрацией по статусу"""
        return get_orders(self.db, skip, limit, status_filter)
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        return get_order(self.db, order_id)
    
    def create_order(self, order_data: OrderCreate, user_id: str) -> Order:
        """Создать новый заказ"""
        return create_order(self.db, order_data, user_id)
    
    def update_order(self, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        """Обновить заказ"""
        return update_order(self.db, order_id, order_data)
    
    def update_order_status(self, order_id: int, status_data: OrderStatusUpdate) -> Optional[Order]:
        """Обновить статус заказа"""
        return update_order_status(self.db, order_id, status_data)
    
    def delete_order(self, order_id: int) -> bool:
        """Удалить заказ"""
        return delete_order(self.db, order_id)
    
    def get_order_statistics(self) -> dict:
        """Получить статистику по заказам"""
        return get_order_statistics(self.db)
    
    def get_orders_by_product(self, product_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить заказы по товару"""
        return get_orders_by_product(self.db, product_id, skip, limit)
    
    def get_orders_by_phone(self, phone: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить заказы по номеру телефона"""
        return get_orders_by_phone(self.db, phone, skip, limit)
    
    def get_last_eur_rate(self) -> Decimal:
        """Получить последний курс евро из заказов"""
        return get_last_eur_rate(self.db)

def get_orders(db: Session, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[Order]:
    """Получить список заказов с фильтрацией по статусу"""
    query = db.query(Order)
    
    if status_filter:
        # Преобразуем строковый фильтр в enum
        try:
            status_enum = OrderStatus(status_filter)
            query = query.filter(Order.status == status_enum)
        except ValueError:
            # Если статус неверный, возвращаем пустой список
            return []
    
    # Сортируем по дате создания (новые сначала)
    query = query.order_by(Order.created_at.desc())
    
    orders = query.offset(skip).limit(limit).all()
    
    # Добавляем вычисленные поля
    for order in orders:
        order.total_amount = order.qty * order.unit_price_rub
        if order.product:
            order.product_name = order.product.name
    
    return orders

def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Получить заказ по ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.total_amount = order.qty * order.unit_price_rub
        if order.product:
            order.product_name = order.product.name
    return order

def create_order(db: Session, order_data: OrderCreate, user_id: str) -> Order:
    """Создать новый заказ"""
    # Проверяем существование товара
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    
    # Проверяем достаточность остатка
    current_stock = calculate_stock(product, db)
    if current_stock < order_data.qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Недостаточно товара на складе. Доступно: {current_stock}, запрошено: {order_data.qty}"
        )
    
    # Создаем заказ
    order = Order(
        phone=order_data.phone,
        customer_name=order_data.customer_name,
        client_city=order_data.client_city,
        product_id=order_data.product_id,
        product_name=product.name,
        qty=order_data.qty,
        unit_price_rub=order_data.unit_price_rub,
        eur_rate=order_data.eur_rate,
        payment_method=order_data.payment_method,
        payment_note=order_data.payment_note,
        status=OrderStatus.PAID_NOT_ISSUED,
        user_id=user_id,
        # Новые поля
        order_code=order_data.order_code,
        order_code_last4=order_data.order_code[-4:] if order_data.order_code else None,
        payment_method_id=order_data.payment_method_id,
        payment_instrument_id=order_data.payment_instrument_id,
        paid_amount=order_data.paid_amount,
        paid_at=order_data.paid_at,
        source=order_data.source or "manual"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Добавляем вычисленные поля
    order.total_amount = order.qty * order.unit_price_rub
    order.product_name = product.name
    
    return order

def update_order(db: Session, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
    """Обновить заказ"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    # Если изменяется количество, проверяем остаток
    if order_data.qty and order_data.qty != order.qty:
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            current_stock = calculate_stock(product, db)
            # Учитываем текущий заказ в остатке
            available_stock = current_stock + order.qty
            if available_stock < order_data.qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно товара на складе. Доступно: {available_stock}, запрошено: {order_data.qty}"
                )
    
    # Обновляем поля
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Обновляем название товара если изменился товар
    if order_data.product_id and order_data.product_id != order.product_id:
        product = db.query(Product).filter(Product.id == order_data.product_id).first()
        if product:
            order.product_name = product.name
    
    db.commit()
    db.refresh(order)
    
    # Добавляем вычисленные поля
    order.total_amount = order.qty * order.unit_price_rub
    if order.product:
        order.product_name = order.product.name
    
    return order

def update_order_status(db: Session, order_id: int, status_data: OrderStatusUpdate) -> Optional[Order]:
    """Обновить статус заказа"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    
    old_status = order.status
    new_status = status_data.status
    
    # Обновляем статус
    order.status = new_status
    
    # Если заказ выдается, устанавливаем время выдачи
    if new_status == OrderStatus.PAID_ISSUED and old_status != OrderStatus.PAID_ISSUED:
        order.issued_at = datetime.now(timezone.utc)
    
    # Если заказ отменяется, сбрасываем время выдачи
    if new_status == OrderStatus.PAID_DENIED and old_status == OrderStatus.PAID_ISSUED:
        order.issued_at = None
    
    # ЛОГИКА УМЕНЬШЕНИЯ ОСТАТКОВ:
    # Уменьшаем остаток только при переходе на статус "оплачен" или "выдан"
    # и только для заказов из магазина (source="shop")
    if (order.source == "shop" and 
        old_status in [OrderStatus.PAID_NOT_ISSUED, OrderStatus.UNPAID] and
        new_status in [OrderStatus.PAID_NOT_ISSUED, OrderStatus.PAID_ISSUED]):
        
        # Получаем товар
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            # Уменьшаем остаток
            product.quantity = max(0, product.quantity - order.qty)
    
    # Если заказ отменяется или переводится в "не оплачен", возвращаем остаток
    if (order.source == "shop" and 
        old_status in [OrderStatus.PAID_NOT_ISSUED, OrderStatus.PAID_ISSUED] and
        new_status in [OrderStatus.UNPAID, OrderStatus.PAID_DENIED]):
        
        # Получаем товар
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            # Возвращаем остаток
            product.quantity += order.qty
    
    db.commit()
    db.refresh(order)
    
    # Добавляем вычисленные поля
    order.total_amount = order.qty * order.unit_price_rub
    if order.product:
        order.product_name = order.product.name
    
    return order

def delete_order(db: Session, order_id: int) -> bool:
    """Удалить заказ"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return False
    
    # Проверяем, можно ли удалить заказ
    if order.status == OrderStatus.PAID_ISSUED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить выданный заказ"
        )
    
    db.delete(order)
    db.commit()
    return True

def get_order_statistics(db: Session) -> dict:
    """Получить статистику по заказам"""
    total_orders = db.query(func.count(Order.id)).scalar()
    pending_count = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PAID_NOT_ISSUED).scalar()
    issued_count = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PAID_ISSUED).scalar()
    denied_count = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PAID_DENIED).scalar()
    
    # Общая сумма выданных заказов
    total_revenue = db.query(func.coalesce(func.sum(Order.qty * Order.unit_price_rub), 0)).filter(
        Order.status == OrderStatus.PAID_ISSUED
    ).scalar()
    
    return {
        "total_orders": total_orders,
        "pending_count": pending_count,
        "issued_count": issued_count,
        "denied_count": denied_count,
        "total_revenue": total_revenue or Decimal('0')
    }

def get_orders_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Получить заказы по товару"""
    orders = db.query(Order).filter(Order.product_id == product_id).offset(skip).limit(limit).all()
    
    for order in orders:
        order.total_amount = order.qty * order.unit_price_rub
        if order.product:
            order.product_name = order.product.name
    
    return orders

def get_orders_by_phone(db: Session, phone: str, skip: int = 0, limit: int = 100) -> List[Order]:
    """Получить заказы по номеру телефона"""
    orders = db.query(Order).filter(Order.phone == phone).offset(skip).limit(limit).all()
    
    for order in orders:
        order.total_amount = order.qty * order.unit_price_rub
        if order.product:
            order.product_name = order.product.name
    
    return orders


def get_last_eur_rate(db: Session) -> Decimal:
    """Получить последний курс евро из заказов"""
    from sqlalchemy import select
    last_order = db.query(Order.eur_rate).order_by(Order.created_at.desc()).first()
    return last_order[0] if last_order else Decimal("90.0000")
