#!/usr/bin/env python3
"""
Скрипт для обновления существующих кодов заказов на новый формат: 3 буквы + 5 цифр
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.order import Order
import random
import string

def generate_new_order_code(existing_codes):
    """Генерирует новый код заказа в формате: 3 буквы + 5 цифр"""
    while True:
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        digits = ''.join(random.choices(string.digits, k=5))
        new_code = letters + digits
        
        if new_code not in existing_codes:
            return new_code

def update_order_codes():
    """Обновляет существующие коды заказов на новый формат"""
    db = SessionLocal()
    
    try:
        # Получаем все заказы с кодами
        orders_with_codes = db.query(Order).filter(Order.order_code.is_not(None)).all()
        
        if not orders_with_codes:
            print("Заказы с кодами не найдены!")
            return
        
        print(f"Найдено {len(orders_with_codes)} заказов с кодами")
        
        # Получаем существующие коды для проверки уникальности
        existing_codes = set()
        for order in orders_with_codes:
            if order.order_code:
                existing_codes.add(order.order_code)
        
        # Обновляем коды для каждого заказа
        updated_count = 0
        for order in orders_with_codes:
            old_code = order.order_code
            new_code = generate_new_order_code(existing_codes)
            
            order.order_code = new_code
            order.order_code_last4 = new_code[-4:]  # Обновляем last4
            
            existing_codes.add(new_code)
            print(f"Заказ {order.id}: {old_code} → {new_code}")
            updated_count += 1
        
        db.commit()
        print(f"Успешно обновлено {updated_count} кодов заказов!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_order_codes()
