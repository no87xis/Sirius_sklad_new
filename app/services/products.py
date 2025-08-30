from sqlalchemy.orm import Session
from sqlalchemy import func, exc
from typing import List, Optional
from ..models import Product, Supply, Order, OrderStatus
from ..schemas.product import ProductCreate, ProductUpdate
from ..schemas.supply import SupplyCreate
from fastapi import HTTPException, status
import random
import string


class ProductService:


    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        db_product = Product(
            name=product.name,
            description=product.description,
            detailed_description=product.detailed_description,
            min_stock=product.min_stock,
            buy_price_eur=product.buy_price_eur,
            sell_price_rub=product.sell_price_rub,
            supplier_name=product.supplier_name,
            quantity=product.initial_quantity
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def get_product(db: Session, product_id: int):
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def update_product(db: Session, product_id: int, product: ProductUpdate):
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return None
        
        update_data = product.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            return False
        
        db.delete(db_product)
        db.commit()
        return True

    @staticmethod
    def get_low_stock_products(db: Session):
        """Получает товары с низким остатком"""
        return db.query(Product).filter(Product.quantity <= Product.min_stock).all()

    @staticmethod
    def get_stock_summary(db: Session):
        """Получает сводку по остаткам товаров"""
        total_products = db.query(func.count(Product.id)).scalar()
        low_stock_count = db.query(func.count(Product.id)).filter(Product.quantity <= Product.min_stock).scalar()
        out_of_stock_count = db.query(func.count(Product.id)).filter(Product.quantity == 0).scalar()
        
        return {
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count
        }


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
    from sqlalchemy.orm import joinedload
    products = db.query(Product).options(joinedload(Product.photos)).offset(skip).limit(limit).all()
    
    # Вычисляем остатки для каждого товара
    for product in products:
        stock = calculate_stock(product, db)
        product.stock = stock
        product.is_low_stock = is_low_stock(product, stock)
    
    return products


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Получить товар по ID с вычисленным остатком"""
    from sqlalchemy.orm import joinedload
    product = db.query(Product).options(joinedload(Product.photos)).filter(Product.id == product_id).first()
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


def delete_product(db: Session, product_id: int, force: bool = False) -> bool:
    """Удалить товар
    
    Args:
        db: Сессия БД
        product_id: ID товара
        force: Принудительное удаление (игнорирует активные заказы)
    """
    print(f"🔍 Попытка удаления товара ID: {product_id} (force={force})")  # Отладка
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        print(f"❌ Товар с ID {product_id} не найден")  # Отладка
        return False
    
    print(f"✅ Товар найден: {product.name}")  # Отладка
    
    try:
        # Проверяем, есть ли активные заказы (не отмененные)
        active_orders = db.query(Order).filter(
            Order.product_id == product_id,
            Order.status != OrderStatus.PAID_DENIED
        ).first()
        
        if active_orders and not force:
            print(f"❌ Найдены активные заказы для товара {product_id}")  # Отладка
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить товар с активными заказами. Сначала отмените все заказы или используйте принудительное удаление."
            )
        
        if active_orders and force:
            print(f"⚠️ Принудительное удаление товара {product_id} с активными заказами")  # Отладка
        
        print(f"✅ Удаляем товар {product.name}")  # Отладка
        db.delete(product)
        db.commit()
        print(f"✅ Товар {product.name} успешно удален")  # Отладка
        return True
        
    except exc.IntegrityError as e:
        db.rollback()
        print(f"❌ FK ошибка при удалении товара {product_id}: {e}")  # Отладка
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Товар связан с заказами или поставками и не может быть удален"
        )
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при удалении товара {product_id}: {e}")  # Отладка
        raise e


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


def update_product_quantity(db: Session, product_id: int, new_quantity: int) -> bool:
    """Обновляет количество товара (ручное изменение)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    
    # Обновляем количество
    product.quantity = new_quantity
    
    # Автоматически обновляем статус наличия
    if new_quantity > 0:
        product.availability_status = 'IN_STOCK'
    else:
        product.availability_status = 'OUT_OF_STOCK'
    
    db.commit()
    db.refresh(product)
    return True
