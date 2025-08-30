#!/usr/bin/env python3
"""
Скрипт для очистки всех тестовых данных из системы Сириус
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models import User, Product, Supply, Order, OperationLog, UserRole
from app.services.auth import get_password_hash

def clear_test_data():
    """Очистка всех тестовых данных из системы"""
    db = SessionLocal()
    
    try:
        print("🧹 Очистка тестовых данных из системы Сириус...")
        
        # 1. Очистка логов операций
        print("Удаление логов операций...")
        deleted_logs = db.query(OperationLog).delete()
        print(f"✅ Удалено {deleted_logs} логов операций")
        
        # 2. Очистка заказов
        print("Удаление заказов...")
        deleted_orders = db.query(Order).delete()
        print(f"✅ Удалено {deleted_orders} заказов")
        
        # 3. Очистка поставок
        print("Удаление поставок...")
        deleted_supplies = db.query(Supply).delete()
        print(f"✅ Удалено {deleted_supplies} поставок")
        
        # 4. Очистка товаров
        print("Удаление товаров...")
        deleted_products = db.query(Product).delete()
        print(f"✅ Удалено {deleted_products} товаров")
        
        # 5. Очистка пользователей (кроме admin)
        print("Удаление тестовых пользователей...")
        test_users = db.query(User).filter(User.username != "admin").all()
        deleted_users = 0
        for user in test_users:
            db.delete(user)
            deleted_users += 1
        print(f"✅ Удалено {deleted_users} тестовых пользователей")
        
        # 6. Проверяем, что admin пользователь существует, если нет - создаем
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Создание пользователя admin...")
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            print("✅ Пользователь admin создан: admin / admin123")
        else:
            print("ℹ️  Пользователь admin уже существует")
        
        # Подтверждаем изменения
        db.commit()
        
        print("\n🎯 База данных успешно очищена!")
        print("\nОставшиеся данные:")
        print(f"  - Пользователи: {db.query(User).count()}")
        print(f"  - Товары: {db.query(Product).count()}")
        print(f"  - Поставки: {db.query(Supply).count()}")
        print(f"  - Заказы: {db.query(Order).count()}")
        print(f"  - Логи операций: {db.query(OperationLog).count()}")
        
        print("\n🔑 Доступ для входа:")
        print("  admin / admin123")
        
        print("\n✨ Теперь вы можете начать заполнять базу данных с чистого листа!")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_test_data()
