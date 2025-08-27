#!/usr/bin/env python3
"""Минимальная инициализация системы Сириус без демо-данных"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Base, engine, SessionLocal
from app import models  # регистрируем declarative models в metadata
from app.models import User, UserRole
from app.services.auth import get_password_hash

def main():
    print("🚀 Минимальная инициализация системы Сириус...")
    
    # Создаем таблицы
    print("📊 Создание таблиц базы данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    # Создаем пользователя admin
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            ))
            db.commit()
            print("✅ Пользователь admin создан: admin / admin123")
        else:
            print("ℹ️  Пользователь admin уже существует")
            
        print("\n🎯 Система готова к запуску!")
        print("🔑 Логин: admin / admin123")
        print("🌐 Запуск: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
