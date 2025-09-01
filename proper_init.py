#!/usr/bin/env python3
"""
Правильная инициализация базы данных Sirius Group
Использует SQLAlchemy без костылей
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Импорт модулей...")
    
    # Импортируем Base и engine
    from app.db import Base, engine
    
    print("✅ Base и engine импортированы")
    
    # Импортируем все модели для регистрации в Base
    from app.models.user import User, UserRole
    from app.models.product import Product
    from app.models.order import Order
    from app.models.shop_cart import ShopCart
    from app.models.product_photo import ProductPhoto
    
    print("✅ Все модели импортированы")
    
    # Создаем все таблицы
    print("🔨 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    # Создаем админа
    print("👤 Создание админа...")
    from app.db import SessionLocal
    from app.services.auth import get_password_hash
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                hashed_password=get_password_hash('admin123'),
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print('✅ Админ создан: admin / admin123')
        else:
            print('✅ Админ уже существует')
    finally:
        db.close()
    
    print("🎉 База данных инициализирована успешно!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
