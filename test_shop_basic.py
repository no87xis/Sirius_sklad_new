#!/usr/bin/env python3
"""
Базовый тест функциональности магазина
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import Product, ProductPhoto, ShopCart, ShopOrder
from app.services.shop_cart import ShopCartService
from app.services.shop_orders import ShopOrderService
from app.services.order_code import OrderCodeService

def test_shop_basic():
    """Тестирует базовую функциональность магазина"""
    print("🧪 Тестирование модуля магазина...")
    
    db = SessionLocal()
    
    try:
        # 1. Проверяем наличие товаров
        products = db.query(Product).all()
        print(f"✅ Товаров в базе: {len(products)}")
        
        if not products:
            print("⚠️  Нет товаров для тестирования!")
            return
        
        # 2. Проверяем генерацию кодов заказов
        test_codes = []
        for _ in range(5):
            code = OrderCodeService.generate_order_code()
            test_codes.append(code)
            print(f"   Код заказа: {code}")
        
        # Проверяем уникальность
        if len(set(test_codes)) == len(test_codes):
            print("✅ Коды заказов уникальны")
        else:
            print("❌ Обнаружены дублирующиеся коды!")
        
        # 3. Проверяем сервис корзины
        test_session = "test_session_123"
        
        # Добавляем товар в корзину
        cart_data = {
            "product_id": products[0].id,
            "quantity": 2,
            "session_id": test_session
        }
        
        try:
            from app.schemas.shop_cart import ShopCartCreate
            cart_item = ShopCartService.add_to_cart(db, ShopCartCreate(**cart_data))
            print(f"✅ Товар добавлен в корзину: ID {cart_item.id}")
            
            # Получаем корзину
            cart_summary = ShopCartService.get_cart_summary(db, test_session)
            print(f"✅ Корзина получена: {cart_summary.total_items} товаров на {cart_summary.total_amount} ₽")
            
            # Очищаем тестовую корзину
            ShopCartService.clear_cart(db, test_session)
            print("✅ Тестовая корзина очищена")
            
        except Exception as e:
            print(f"❌ Ошибка работы с корзиной: {e}")
        
        # 4. Проверяем сервис заказов
        try:
            # Получаем истёкшие заказы
            expired_orders = ShopOrderService.get_expired_orders(db)
            print(f"✅ Истёкших заказов: {len(expired_orders)}")
            
            # Получаем аналитику
            analytics = ShopOrderService.get_analytics(db)
            print(f"✅ Аналитика получена: {analytics.total_orders} заказов")
            
        except Exception as e:
            print(f"❌ Ошибка работы с заказами: {e}")
        
        print("\n🎯 Базовое тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_shop_basic()
