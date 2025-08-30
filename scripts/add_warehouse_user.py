#!/usr/bin/env python3
"""
Скрипт для добавления пользователя с ролью warehouse в систему Сириус
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models import User, UserRole
from app.services.auth import get_password_hash

def add_warehouse_user():
    """Добавление пользователя с ролью warehouse в систему"""
    db = SessionLocal()
    
    try:
        print("👷 Добавление работника склада в систему Сириус...")
        
        # Создание таблиц, если их нет
        Base.metadata.create_all(bind=engine)
        
        # Создаем работника склада с ролью WAREHOUSE
        warehouse_worker = User(
            username="warehouse_worker",
            hashed_password=get_password_hash("warehouse123"),
            role=UserRole.WAREHOUSE
        )
        
        # Проверяем, не существует ли уже
        existing_user = db.query(User).filter(User.username == "warehouse_worker").first()
        if existing_user:
            print("ℹ️  Пользователь warehouse_worker уже существует")
        else:
            db.add(warehouse_worker)
            print("✅ Создан работник склада warehouse_worker: warehouse_worker / warehouse123")
            print("   Роль: WAREHOUSE - расширенные права для работы со складом")
        
        # Подтверждаем изменения
        db.commit()
        
        print("\n🎯 Работник склада успешно добавлен!")
        print("\nДоступные пользователи:")
        print("  admin / admin123 - Администратор (полный доступ)")
        print("  sklad_manager / sklad123 - Менеджер склада (управление статусами)")
        print("  sklad_operator / operator123 - Оператор склада (заказы и выдача)")
        print("  warehouse_worker / warehouse123 - Работник склада (новая роль WAREHOUSE)")
        
        print("\n📋 Возможности по ролям:")
        print("  ADMIN: Полный доступ ко всем функциям")
        print("  MANAGER: Управление заказами, изменение статусов, просмотр аналитики")
        print("  USER: Создание заказов, выдача товаров, просмотр товаров")
        print("  WAREHOUSE: Расширенные возможности склада + создание заказов с кодами")
        
        print("\n✨ Теперь у вас есть пользователь с новой ролью WAREHOUSE!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении работника: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_warehouse_user()
