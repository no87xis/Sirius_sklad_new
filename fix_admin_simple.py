#!/usr/bin/env python3
"""
Простое исправление админа без лишних полей
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db import SessionLocal, engine, Base
from app.models import User
from app.services.auth import get_password_hash

def fix_admin_simple():
    """Создать админа с минимальными полями"""
    try:
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        try:
            # Удаляем старого админа если есть
            db.query(User).filter(User.username == 'admin').delete()
            
            # Создаем нового админа с минимальными полями
            admin_user = User(
                username='admin',
                hashed_password=get_password_hash('admin123'),
                role='admin'
            )
            
            db.add(admin_user)
            db.commit()
            
            print('✅ Админ создан: admin / admin123')
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return False

if __name__ == "__main__":
    fix_admin_simple()
