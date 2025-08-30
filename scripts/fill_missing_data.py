#!/usr/bin/env python3
"""
Скрипт для заполнения недостающих данных после миграции
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models import User, Product, Order, PaymentMethodModel, PaymentInstrument, CashFlow
from app.services.order_code import OrderCodeService
from app.services.payments import PaymentService
from decimal import Decimal
from datetime import datetime

def fill_missing_data():
    """Заполняет недостающие данные после миграции"""
    db = SessionLocal()
    
    try:
        print("🔧 Заполнение недостающих данных после миграции...")
        
        # 1. Создаем базовые методы оплаты
        print("\n1️⃣ Создание методов оплаты...")
        
        payment_methods = [
            {'name': 'Наличные на складе', 'type': 'cash'},
            {'name': 'Перевод на карту', 'type': 'card'},
            {'name': 'USDT', 'type': 'crypto'},
            {'name': 'Банковский перевод', 'type': 'bank'},
            {'name': 'Другой способ', 'type': 'other'}
        ]
        
        created_methods = {}
        for method_data in payment_methods:
            existing = db.query(PaymentMethodModel).filter(PaymentMethodModel.name == method_data['name']).first()
            if not existing:
                method = PaymentMethodModel(
                    name=method_data['name'],
                    type=method_data['type'],
                    is_active=True
                )
                db.add(method)
                db.commit()
                db.refresh(method)
                created_methods[method_data['name']] = method
                print(f"   ✅ Создан метод: {method.name}")
            else:
                created_methods[method_data['name']] = existing
                print(f"   ℹ️  Метод уже существует: {existing.name}")
        
        # 2. Генерируем коды для существующих заказов
        print("\n2️⃣ Генерация кодов для существующих заказов...")
        
        orders_without_code = db.query(Order).filter(Order.order_code.is_(None)).all()
        if orders_without_code:
            for order in orders_without_code:
                order_code = OrderCodeService.generate_unique_order_code(db)
                order.order_code = order_code
                order.order_code_last4 = order_code[-4:]
                
                # Устанавливаем дефолтный метод оплаты
                if not order.payment_method_id:
                    default_method = created_methods.get('Другой способ')
                    if default_method:
                        order.payment_method_id = default_method.id
                
                print(f"   ✅ Заказ #{order.id}: код {order_code}")
        else:
            print("   ℹ️  Все заказы уже имеют коды")
        
        # 3. Устанавливаем дефолтные значения для товаров
        print("\n3️⃣ Установка дефолтных значений для товаров...")
        
        products_without_status = db.query(Product).filter(Product.availability_status.is_(None)).all()
        if products_without_status:
            for product in products_without_status:
                product.availability_status = 'IN_STOCK'
                print(f"   ✅ Товар #{product.id}: статус установлен 'IN_STOCK'")
        else:
            print("   ℹ️  Все товары уже имеют статус")
        
        # 4. Создаем базовые инструменты оплаты
        print("\n4️⃣ Создание базовых инструментов оплаты...")
        
        # Для метода "Перевод на карту" создаем базовую карту
        card_method = created_methods.get('Перевод на карту')
        if card_method:
            existing_card = db.query(PaymentInstrument).filter(
                PaymentInstrument.name == 'Основная карта',
                PaymentInstrument.method_id == card_method.id
            ).first()
            
            if not existing_card:
                card_instrument = PaymentInstrument(
                    name='Основная карта',
                    method_id=card_method.id,
                    is_active=True
                )
                db.add(card_instrument)
                print("   ✅ Создан инструмент: Основная карта")
        
        # 5. Подтверждаем изменения
        db.commit()
        
        print("\n🎯 Заполнение данных завершено успешно!")
        
        # 6. Выводим статистику
        print("\n📊 Статистика после заполнения:")
        print(f"   - Методы оплаты: {db.query(PaymentMethodModel).count()}")
        print(f"   - Инструменты оплаты: {db.query(PaymentInstrument).count()}")
        print(f"   - Заказы с кодами: {db.query(Order).filter(Order.order_code.isnot(None)).count()}")
        print(f"   - Товары со статусом: {db.query(Product).filter(Product.availability_status.isnot(None)).count()}")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении данных: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fill_missing_data()
