#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с авторизацией
"""
from app.db import get_db
from app.services.auth import authenticate_user, get_password_hash
from app.models import User
from sqlalchemy.orm import Session

def check_admin_user():
    """Проверить существование админа"""
    db = next(get_db())
    
    # Проверяем админа
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
        print(f"✅ Админ найден: {admin.username}")
        print(f"   Роль: {admin.role}")
        print(f"   Хэш пароля: {admin.hashed_password[:20]}...")
        
        # Проверяем аутентификацию
        auth_result = authenticate_user(db, "admin", "admin123")
        if auth_result:
            print("✅ Аутентификация admin/admin123 успешна")
        else:
            print("❌ Аутентификация admin/admin123 не удалась")
            
            # Проверяем хэш
            test_hash = get_password_hash("admin123")
            print(f"   Ожидаемый хэш: {test_hash[:20]}...")
            print(f"   Текущий хэш:   {admin.hashed_password[:20]}...")
    else:
        print("❌ Админ не найден")
    
    # Показываем всех пользователей
    users = db.query(User).all()
    print(f"\n📋 Всего пользователей: {len(users)}")
    for user in users:
        print(f"   - {user.username} (роль: {user.role})")
    
    db.close()

if __name__ == "__main__":
    check_admin_user()
