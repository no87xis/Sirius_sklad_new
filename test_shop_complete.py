#!/usr/bin/env python3
"""
Полный тест функциональности магазина
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import Product, ShopCart, ShopOrder
from app.services.shop_cart import ShopCartService
from app.services.shop_orders import ShopOrderService
from app.services.order_code import OrderCodeService

def test_shop_complete():
    """Полный тест функциональности магазина"""
    print("🧪 Полное тестирование модуля магазина...")
    
    db = SessionLocal()
    
    try:
        # 1. Проверяем наличие товаров
        products = db.query(Product).all()
        print(f"✅ Товаров в базе: {len(products)}")
        
        if not products:
            print("⚠️  Нет товаров для тестирования!")
            return
        
        # 2. Тестируем корзину
        print("\n🛒 Тестирование корзины...")
        test_session = "test_session_complete"
        
        # Добавляем несколько товаров в корзину
        cart_items = []
        for i, product in enumerate(products[:2]):  # Берем первые 2 товара
            cart_data = {
                "product_id": product.id,
                "quantity": i + 1,
                "session_id": test_session
            }
            
            from app.schemas.shop_cart import ShopCartCreate
            cart_item = ShopCartService.add_to_cart(db, ShopCartCreate(**cart_data))
            cart_items.append(cart_item)
            print(f"   ✅ Товар '{product.name}' добавлен в корзину (количество: {i + 1})")
        
        # Получаем корзину
        cart_summary = ShopCartService.get_cart_summary(db, test_session)
        print(f"   ✅ Корзина: {cart_summary.total_items} товаров на {cart_summary.total_amount} ₽")
        
        # 3. Тестируем создание заказов
        print("\n📋 Тестирование создания заказов...")
        
        from app.schemas.shop_order import ShopOrderCreate
        order_data = ShopOrderCreate(
            customer_name="Тестовый Клиент",
            customer_phone="+79991234567",
            customer_city="Грозный",
            payment_method_id=1,  # Предполагаем, что есть способ оплаты с ID 1
            cart_items=[{"product_id": item.product_id, "quantity": item.quantity} for item in cart_items]
        )
        
        try:
            orders = ShopOrderService.create_orders_from_cart(db, order_data)
            print(f"   ✅ Создано заказов: {len(orders)}")
            
            for order in orders:
                print(f"      📦 Заказ {order.order_code}: {order.product_name} x{order.quantity} = {order.total_amount} ₽")
                print(f"         Статус: {order.status}")
                print(f"         Резерв до: {order.reserved_until.strftime('%d.%m.%Y %H:%M')}")
            
            # 4. Тестируем поиск заказов
            print("\n🔍 Тестирование поиска заказов...")
            
            from app.schemas.shop_order import ShopOrderSearch
            search_data = ShopOrderSearch(
                order_code=orders[0].order_code,
                customer_phone="+79991234567"
            )
            
            found_orders = ShopOrderService.search_orders(db, search_data)
            print(f"   ✅ Найдено заказов: {len(found_orders)}")
            
            # 5. Тестируем аналитику
            print("\n📊 Тестирование аналитики...")
            
            analytics = ShopOrderService.get_analytics(db)
            print(f"   ✅ Всего заказов: {analytics.total_orders}")
            print(f"   ✅ Общая сумма: {analytics.total_amount} ₽")
            print(f"   ✅ Зарезервировано: {analytics.reserved_not_paid} на {analytics.reserved_not_paid_amount} ₽")
            
            # 6. Тестируем обновление заказа
            print("\n✏️  Тестирование обновления заказа...")
            
            from app.schemas.shop_order import ShopOrderUpdate
            update_data = ShopOrderUpdate(
                status="paid"
            )
            
            updated_order = ShopOrderService.update_order(db, orders[0].id, update_data)
            if updated_order:
                print(f"   ✅ Заказ обновлен: статус изменен на {updated_order.status}")
                print(f"      Время оплаты: {updated_order.paid_at}")
            else:
                print("   ❌ Не удалось обновить заказ")
            
            # 7. Очищаем тестовые данные
            print("\n🧹 Очистка тестовых данных...")
            
            # Удаляем тестовые заказы
            for order in orders:
                db.delete(order)
            
            # Очищаем корзину
            ShopCartService.clear_cart(db, test_session)
            
            db.commit()
            print("   ✅ Тестовые данные очищены")
            
        except Exception as e:
            print(f"   ❌ Ошибка при создании заказов: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎯 Полное тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_shop_complete()
