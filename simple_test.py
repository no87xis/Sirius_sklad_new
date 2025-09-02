#!/usr/bin/env python3
"""
Простой тест для проверки API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_shop_api():
    """Тестируем shop_api"""
    try:
        from app.routers.shop_api import router
        print("✅ shop_api router импортируется")
        
        # Проверяем префикс
        print(f"📝 Префикс роутера: {router.prefix}")
        
        # Проверяем маршруты
        routes = [route.path for route in router.routes]
        print(f"📝 Доступные маршруты: {routes}")
        
        if "/cart/add-form" in routes:
            print("✅ Маршрут /cart/add-form найден")
        else:
            print("❌ Маршрут /cart/add-form НЕ найден")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_main_app():
    """Тестируем main.py"""
    try:
        from app.main import app
        print("✅ main.py импортируется")
        
        # Проверяем подключенные роутеры
        print(f"📝 Всего роутов в приложении: {len(app.routes)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Простой тест API")
    print("=" * 30)
    
    test_shop_api()
    print()
    test_main_app()
