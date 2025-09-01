#!/usr/bin/env python3
"""
Быстрое исправление инициализации базы данных Sirius Group
"""

import sys
import os

# Добавляем путь к проекту
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

try:
    print("🚀 Sirius Group - Быстрое исправление базы данных")
    print("=" * 50)
    
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
    
    # Создаем тестовый продукт с ПРАВИЛЬНЫМИ полями
    print("📦 Создание тестового продукта...")
    try:
        db = SessionLocal()
        try:
            test_product = db.query(Product).filter(Product.name == 'Тестовый продукт').first()
            if not test_product:
                from app.constants import DEFAULT_STATUS
                test_product = Product(
                    name='Тестовый продукт',
                    description='Описание тестового продукта',
                    sell_price_rub=1000.00,  # ПРАВИЛЬНОЕ название поля
                    quantity=100,
                    availability_status=DEFAULT_STATUS
                )
                db.add(test_product)
                db.commit()
                print('✅ Тестовый продукт создан')
            else:
                print('✅ Тестовый продукт уже существует')
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Ошибка создания тестового продукта: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🎉 БАЗА ДАННЫХ ИСПРАВЛЕНА!")
    print("✅ Все таблицы созданы")
    print("✅ Админ создан: admin / admin123")
    print("✅ Тестовый продукт создан")
    print("=" * 50)
    
    return True
    
except Exception as e:
    print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 Исправление не удалось!")
        sys.exit(1)
    else:
        print("\n🚀 Готово к запуску!")
