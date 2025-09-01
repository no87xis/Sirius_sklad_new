#!/usr/bin/env python3
"""
Идеальная инициализация базы данных Sirius Group
Без костылей, с полной обработкой ошибок
"""

import sys
import os
import traceback

def main():
    try:
        print("🚀 Sirius Group - Идеальная инициализация базы данных")
        print("=" * 60)
        
        # Добавляем путь к проекту
        project_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_path)
        print(f"📁 Путь к проекту: {project_path}")
        
        # Шаг 1: Импорт базовых модулей
        print("\n📋 Шаг 1: Импорт базовых модулей...")
        from app.db import Base, engine
        print("✅ Base и engine импортированы")
        
        # Шаг 2: Импорт всех моделей для регистрации в Base
        print("\n📋 Шаг 2: Импорт моделей...")
        try:
            from app.models.user import User, UserRole
            print("✅ User модель импортирована")
        except Exception as e:
            print(f"❌ Ошибка импорта User: {e}")
            return False
            
        try:
            from app.models.product import Product
            print("✅ Product модель импортирована")
        except Exception as e:
            print(f"❌ Ошибка импорта Product: {e}")
            return False
            
        try:
            from app.models.order import Order
            print("✅ Order модель импортирована")
        except Exception as e:
            print(f"❌ Ошибка импорта Order: {e}")
            return False
            
        try:
            from app.models.shop_cart import ShopCart
            print("✅ ShopCart модель импортирована")
        except Exception as e:
            print(f"❌ Ошибка импорта ShopCart: {e}")
            return False
            
        try:
            from app.models.product_photo import ProductPhoto
            print("✅ ProductPhoto модель импортирована")
        except Exception as e:
            print(f"❌ Ошибка импорта ProductPhoto: {e}")
            return False
        
        # Шаг 3: Создание всех таблиц
        print("\n📋 Шаг 3: Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Все таблицы созданы успешно")
        
        # Шаг 4: Создание админа
        print("\n📋 Шаг 4: Создание админа...")
        try:
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
        except Exception as e:
            print(f"❌ Ошибка создания админа: {e}")
            traceback.print_exc()
            return False
        
        # Шаг 5: Создание тестового продукта
        print("\n📋 Шаг 5: Создание тестового продукта...")
        try:
            db = SessionLocal()
            try:
                test_product = db.query(Product).filter(Product.name == 'Тестовый продукт').first()
                if not test_product:
                    from app.constants import DEFAULT_STATUS
                    test_product = Product(
                        name='Тестовый продукт',
                        description='Описание тестового продукта',
                        price_rub=1000.00,
                        stock_quantity=100,
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
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ИДЕАЛЬНАЯ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА!")
        print("✅ База данных создана")
        print("✅ Все таблицы созданы")
        print("✅ Админ создан: admin / admin123")
        print("✅ Тестовый продукт создан")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("\n🔍 Подробности ошибки:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 Инициализация не удалась!")
        sys.exit(1)
    else:
        print("\n🚀 Готово к запуску!")
