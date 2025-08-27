#!/usr/bin/env python3
"""
Скрипт для создания демо-данных в системе Сириус
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models import User, Product, Supply, Order, OperationLog, UserRole
from app.services.auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Создание демо-данных для системы"""
    db = SessionLocal()
    
    try:
        # Создание таблиц
        Base.metadata.create_all(bind=engine)
        
        print("Создание демо-данных для системы Сириус...")
        
        # 1. Создание пользователей
        print("Создание пользователей...")
        users_data = [
            {
                "username": "admin",
                "password": "admin123",
                "role": UserRole.ADMIN
            },
            {
                "username": "manager",
                "password": "manager123", 
                "role": UserRole.MANAGER
            },
            {
                "username": "operator",
                "password": "operator123",
                "role": UserRole.USER
            },
            {
                "username": "ivanov",
                "password": "ivanov123",
                "role": UserRole.USER
            },
            {
                "username": "petrov",
                "password": "petrov123",
                "role": UserRole.MANAGER
            }
        ]
        
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.add(user)
        
        db.commit()
        print(f"Создано {len(users_data)} пользователей")
        
        # 2. Создание товаров
        print("Создание товаров...")
        products_data = [
            {
                "name": "Ноутбук Dell Latitude 5520",
                "description": "Бизнес-ноутбук 15.6\", Intel Core i5, 8GB RAM, 256GB SSD",
                "quantity": 15,
                "min_stock": 5,
                "buy_price_eur": 850.0,
                "sell_price_rub": 95000.0,
                "supplier_name": "Dell Technologies"
            },
            {
                "name": "Монитор Samsung 24\"",
                "description": "Монитор 24\" Full HD, IPS, HDMI, VGA",
                "quantity": 25,
                "min_stock": 8,
                "buy_price_eur": 120.0,
                "sell_price_rub": 15000.0,
                "supplier_name": "Samsung Electronics"
            },
            {
                "name": "Клавиатура Logitech K780",
                "description": "Беспроводная клавиатура с подсветкой, мультиустройство",
                "quantity": 40,
                "min_stock": 10,
                "buy_price_eur": 45.0,
                "sell_price_rub": 5500.0,
                "supplier_name": "Logitech"
            },
            {
                "name": "Мышь Logitech MX Master 3",
                "description": "Беспроводная мышь с точным сенсором, эргономичная",
                "quantity": 30,
                "min_stock": 8,
                "buy_price_eur": 65.0,
                "sell_price_rub": 7500.0,
                "supplier_name": "Logitech"
            },
            {
                "name": "Принтер HP LaserJet Pro",
                "description": "Лазерный принтер A4, монохромный, 25 стр/мин",
                "quantity": 8,
                "min_stock": 3,
                "buy_price_eur": 280.0,
                "sell_price_rub": 32000.0,
                "supplier_name": "HP Inc."
            },
            {
                "name": "Сканер Canon CanoScan",
                "description": "Планшетный сканер A4, 4800 DPI, USB",
                "quantity": 12,
                "min_stock": 4,
                "buy_price_eur": 95.0,
                "sell_price_rub": 11500.0,
                "supplier_name": "Canon"
            },
            {
                "name": "USB-флешка Kingston 32GB",
                "description": "USB 3.0 флешка 32GB, высокая скорость чтения/записи",
                "quantity": 100,
                "min_stock": 20,
                "buy_price_eur": 8.0,
                "sell_price_rub": 1200.0,
                "supplier_name": "Kingston Technology"
            },
            {
                "name": "Внешний HDD Seagate 1TB",
                "description": "Внешний жесткий диск 1TB, USB 3.0, портативный",
                "quantity": 20,
                "min_stock": 6,
                "buy_price_eur": 55.0,
                "sell_price_rub": 6500.0,
                "supplier_name": "Seagate Technology"
            },
            {
                "name": "Сетевая карта Intel Gigabit",
                "description": "Сетевая карта PCI-E, Gigabit Ethernet, 10/100/1000 Mbps",
                "quantity": 35,
                "min_stock": 10,
                "buy_price_eur": 25.0,
                "sell_price_rub": 3000.0,
                "supplier_name": "Intel Corporation"
            },
            {
                "name": "Блок питания Corsair 650W",
                "description": "Блок питания 650W, 80+ Bronze, модульный",
                "quantity": 18,
                "min_stock": 5,
                "buy_price_eur": 75.0,
                "sell_price_rub": 9000.0,
                "supplier_name": "Corsair"
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product(**product_data)
            db.add(product)
            products.append(product)
        
        db.commit()
        print(f"Создано {len(products_data)} товаров")
        
        # 3. Создание поставок
        print("Создание поставок...")
        suppliers = ["Dell Technologies", "Samsung Electronics", "Logitech", "HP Inc.", "Canon", 
                    "Kingston Technology", "Seagate Technology", "Intel Corporation", "Corsair"]
        
        supplies = []
        for i in range(20):
            product = random.choice(products)
            supplier = random.choice(suppliers)
            qty = random.randint(5, 50)
            buy_price = product.buy_price_eur * random.uniform(0.8, 1.2)  # ±20% от базовой цены
            
            supply = Supply(
                product_id=product.id,
                supplier_name=supplier,
                qty=qty,
                buy_price_eur=buy_price,
                delivery_date=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(supply)
            supplies.append(supply)
        
        db.commit()
        print(f"Создано {len(supplies)} поставок")
        
        # 4. Создание заказов
        print("Создание заказов...")
        customers = [
            {"name": "ООО 'ТехноСервис'", "phone": "+7-495-123-45-67"},
            {"name": "ИП Иванов А.А.", "phone": "+7-916-234-56-78"},
            {"name": "ООО 'ИнфоТех'", "phone": "+7-495-345-67-89"},
            {"name": "АО 'СтройМонтаж'", "phone": "+7-495-456-78-90"},
            {"name": "ООО 'Медицинские системы'", "phone": "+7-495-567-89-01"},
            {"name": "ИП Петров В.В.", "phone": "+7-916-678-90-12"},
            {"name": "ООО 'Образовательные технологии'", "phone": "+7-495-789-01-23"},
            {"name": "АО 'ФинансИнвест'", "phone": "+7-495-890-12-34"}
        ]
        
        users = db.query(User).filter(User.role.in_([UserRole.USER, UserRole.MANAGER])).all()
        
        orders = []
        for i in range(15):
            customer = random.choice(customers)
            user = random.choice(users)
            product = random.choice(products)
            qty = random.randint(1, 5)
            
            order = Order(
                customer_name=customer["name"],
                customer_phone=customer["phone"],
                product_id=product.id,
                qty=qty,
                user_id=user.username,
                issue_date=datetime.now() - timedelta(days=random.randint(1, 60)),
                status="issued"
            )
            db.add(order)
            orders.append(order)
        
        db.commit()
        print(f"Создано {len(orders)} заказов")
        
        # 5. Создание логов операций
        print("Создание логов операций...")
        log_actions = ["create", "update", "delete", "issue", "deny"]
        entity_types = ["user", "product", "order", "supply"]
        
        for i in range(50):
            user = random.choice(users)
            action = random.choice(log_actions)
            entity_type = random.choice(entity_types)
            entity_id = str(random.randint(1, 100))
            
            details_map = {
                "user": {
                    "create": "Создан новый пользователь",
                    "update": "Обновлены данные пользователя",
                    "delete": "Удален пользователь"
                },
                "product": {
                    "create": "Добавлен новый товар",
                    "update": "Обновлены данные товара",
                    "delete": "Удален товар"
                },
                "order": {
                    "create": "Создан новый заказ",
                    "update": "Обновлен заказ",
                    "delete": "Отменен заказ",
                    "issue": "Выдан заказ клиенту",
                    "deny": "Отказано в выдаче заказа"
                },
                "supply": {
                    "create": "Зарегистрирована поставка",
                    "update": "Обновлены данные поставки",
                    "delete": "Отменена поставка"
                }
            }
            
            details = details_map.get(entity_type, {}).get(action, f"Операция {action} над {entity_type}")
            
            log = OperationLog(
                user_id=user.username,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details
            )
            db.add(log)
        
        db.commit()
        print(f"Создано 50 логов операций")
        
        print("\n✅ Демо-данные успешно созданы!")
        print("\nДоступные пользователи:")
        print("  admin/admin123 - Администратор")
        print("  manager/manager123 - Менеджер")
        print("  operator/operator123 - Оператор")
        print("  ivanov/ivanov123 - Пользователь")
        print("  petrov/petrov123 - Менеджер")
        
        print(f"\nСоздано:")
        print(f"  - {len(users_data)} пользователей")
        print(f"  - {len(products_data)} товаров")
        print(f"  - {len(supplies)} поставок")
        print(f"  - {len(orders)} заказов")
        print(f"  - 50 логов операций")
        
    except Exception as e:
        print(f"❌ Ошибка при создании демо-данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
