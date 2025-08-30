#!/usr/bin/env python3
"""
Скрипт для заполнения существующих товаров уникальными кодами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.product import Product
import random
import string

def generate_unique_product_code(db, existing_codes):
    """Генерирует уникальный код товара"""
    while True:
        letter = random.choice(string.ascii_uppercase)
        digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        product_code = f"{letter}{digits}"
        
        if product_code not in existing_codes:
            return product_code

def fill_product_codes():
    """Заполняет существующие товары уникальными кодами"""
    db = SessionLocal()
    
    try:
        # Получаем все товары без кодов
        products_without_codes = db.query(Product).filter(Product.product_code.is_(None)).all()
        
        if not products_without_codes:
            print("Все товары уже имеют коды!")
            return
        
        print(f"Найдено {len(products_without_codes)} товаров без кодов")
        
        # Получаем существующие коды
        existing_codes = set()
        products_with_codes = db.query(Product).filter(Product.product_code.is_not(None)).all()
        for product in products_with_codes:
            existing_codes.add(product.product_code)
        
        # Заполняем коды для товаров без них
        for product in products_without_codes:
            product_code = generate_unique_product_code(db, existing_codes)
            product.product_code = product_code
            existing_codes.add(product_code)
            print(f"Товар '{product.name}' получил код: {product_code}")
        
        db.commit()
        print(f"Успешно заполнено {len(products_without_codes)} товаров!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fill_product_codes()
