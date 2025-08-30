#!/usr/bin/env python3
"""
Скрипт для добавления работников склада в систему Сириус
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models import User, UserRole
from app.services.auth import get_password_hash

def add_warehouse_workers():
    """Добавление работников склада в систему"""
    db = SessionLocal()
    
    try:
        print("👷 Добавление работников склада в систему Сириус...")
        
        # Создание таблиц, если их нет
        Base.metadata.create_all(bind=engine)
        
        # 1. Работник склада для изменения статусов заказов (MANAGER)
        print("Добавление работника склада для управления статусами...")
        warehouse_manager = User(
            username="sklad_manager",
            hashed_password=get_password_hash("sklad123"),
            role=UserRole.MANAGER
        )
        
        # Проверяем, не существует ли уже
        existing_user = db.query(User).filter(User.username == "sklad_manager").first()
        if existing_user:
            print("ℹ️  Пользователь sklad_manager уже существует")
        else:
            db.add(warehouse_manager)
            print("✅ Создан работник склада sklad_manager: sklad_manager / sklad123")
            print("   Роль: MANAGER - может изменять статусы заказов")
        
        # 2. Работник склада для создания заказов и выдачи товаров (USER)
        print("Добавление работника склада для заказов и выдачи...")
        warehouse_operator = User(
            username="sklad_operator",
            hashed_password=get_password_hash("operator123"),
            role=UserRole.USER
        )
        
        # Проверяем, не существует ли уже
        existing_user = db.query(User).filter(User.username == "sklad_operator").first()
        if existing_user:
            print("ℹ️  Пользователь sklad_operator уже существует")
        else:
            db.add(warehouse_operator)
            print("✅ Создан работник склада sklad_operator: sklad_operator / operator123")
            print("   Роль: USER - может создавать заказы и выдавать товары")
        
        # Подтверждаем изменения
        db.commit()
        
        print("\n🎯 Работники склада успешно добавлены!")
        print("\nДоступные пользователи:")
        print("  admin / admin123 - Администратор (полный доступ)")
        print("  sklad_manager / sklad123 - Менеджер склада (управление статусами)")
        print("  sklad_operator / operator123 - Оператор склада (заказы и выдача)")
        
        print("\n📋 Возможности по ролям:")
        print("  ADMIN: Полный доступ ко всем функциям")
        print("  MANAGER: Управление заказами, изменение статусов, просмотр аналитики")
        print("  USER: Создание заказов, выдача товаров, просмотр товаров")
        
        print("\n✨ Теперь у вас есть команда для работы со складом!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении работников: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_warehouse_workers()
