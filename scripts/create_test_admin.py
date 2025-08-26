#!/usr/bin/env python3
"""
Скрипт для автоматического создания тестового администратора
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import SessionLocal, engine, Base
from app.models import User
from app.services.auth import get_password_hash

def create_test_admin():
    """Создать тестового администратора"""
    db = SessionLocal()
    try:
        # Создаем таблицы, если их нет
        Base.metadata.create_all(bind=engine)
        
        username = "admin"
        password = "admin123"
        
        # Проверяем, существует ли уже пользователь
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Пользователь {username} уже существует!")
            return False
        
        # Создаем нового администратора
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            hashed_password=hashed_password,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Тестовый администратор успешно создан!")
        print(f"Имя пользователя: {username}")
        print(f"Пароль: {password}")
        print("Перейдите на http://localhost:8000/login")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin()
