#!/usr/bin/env python3
"""
Скрипт для создания первого администратора системы
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import SessionLocal, engine, Base
from app.models import User
from app.services.auth import get_password_hash

def create_admin_user(username: str, password: str):
    """Создать пользователя с ролью администратора"""
    db = SessionLocal()
    try:
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
        
        print(f"Администратор {username} успешно создан!")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Основная функция"""
    print("Создание первого администратора системы 'Сириус'")
    print("=" * 50)
    
    # Создаем таблицы, если их нет
    Base.metadata.create_all(bind=engine)
    
    username = input("Введите имя пользователя для администратора: ").strip()
    if not username:
        print("Имя пользователя не может быть пустым!")
        return
    
    password = input("Введите пароль: ").strip()
    if not password:
        print("Пароль не может быть пустым!")
        return
    
    confirm_password = input("Подтвердите пароль: ").strip()
    if password != confirm_password:
        print("Пароли не совпадают!")
        return
    
    if create_admin_user(username, password):
        print("\nТеперь вы можете войти в систему как администратор!")
        print(f"Имя пользователя: {username}")
        print("Перейдите на http://localhost:8000/login")
    else:
        print("\nНе удалось создать администратора!")

if __name__ == "__main__":
    main()
