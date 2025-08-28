from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..models import Product, Supply, Order, OrderStatus
from ..schemas.product import ProductCreate, ProductUpdate
from ..schemas.supply import SupplyCreate
from fastapi import HTTPException, status


def calculate_stock(product: Product, db: Session) -> int:
    """Вычислить текущий остаток товара"""
    # Получаем количество выданных заказов
    issued_orders = db.query(func.coalesce(func.sum(Order.qty), 0)).filter(
        Order.product_id == product.id,
        Order.status == OrderStatus.PAID_ISSUED
    ).scalar()
    
    # Остаток = общий приход - выданные заказы
    stock = product.quantity - issued_orders
    return max(0, stock)


def is_low_stock(product: Product, stock: int) -> bool:
    """Проверить, низкий ли остаток"""
    return stock < product.min_stock


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Получить список товаров с вычисленными остатками"""
    products = db.query(Product).offset(skip).limit(limit).all()
    
    # Вычисляем остатки для каждого товара
    for product in products:
        stock = calculate_stock(product, db)
        product.stock = stock
        product.is_low_stock = is_low_stock(product, stock)
    
    return products


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Получить товар по ID с вычисленным остатком"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        stock = calculate_stock(product, db)
        product.stock = stock
        product.is_low_stock = is_low_stock(product, stock)
    return product


def create_product(db: Session, product_data: ProductCreate) -> Product:
    """Создать новый товар"""
    # Проверяем уникальность имени
    existing_product = db.query(Product).filter(Product.name == product_data.name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Товар с таким именем уже существует"
        )
    
    # Создаем товар
    product = Product(
        name=product_data.name,
        description=product_data.description,
        min_stock=product_data.min_stock,
        buy_price_eur=product_data.buy_price_eur,
        sell_price_rub=product_data.sell_price_rub,
        supplier_name=product_data.supplier_name,
        quantity=product_data.initial_quantity
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
    """Обновить товар"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    # Обновляем только переданные поля
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


def delete_product(db: Session, product_id: int) -> bool:
    """Удалить товар"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    
    # Проверяем, есть ли активные заказы
    active_orders = db.query(Order).filter(
        Order.product_id == product_id,
        Order.status.in_([OrderStatus.PAID_NOT_ISSUED, OrderStatus.PAID_ISSUED])
    ).first()
    
    if active_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить товар с активными заказами"
        )
    
    db.delete(product)
    db.commit()
    return True


def create_supply(db: Session, supply_data: SupplyCreate) -> Supply:
    """Создать поставку и обновить остаток товара"""
    # Проверяем существование товара
    product = db.query(Product).filter(Product.id == supply_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Создаем поставку
    supply = Supply(
        product_id=supply_data.product_id,
        qty=supply_data.qty,
        supplier_name=supply_data.supplier_name,
        buy_price_eur=supply_data.buy_price_eur
    )
    
    db.add(supply)
    
    # Обновляем остаток товара
    product.quantity += supply_data.qty
    
    db.commit()
    db.refresh(supply)
    
    return supply


def get_product_supplies(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Supply]:
    """Получить поставки товара"""
    supplies = db.query(Supply).filter(
        Supply.product_id == product_id
    ).offset(skip).limit(limit).all()
    
    # Добавляем название товара
    for supply in supplies:
        if supply.product:
            supply.product_name = supply.product.name
    
    return supplies
