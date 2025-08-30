#!/usr/bin/env python3
"""Тест новой логики заказов магазина"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def main():
    print("🧪 Тестирование новой логики заказов магазина")
    print("=" * 50)
    
    # Создаем сессию для сохранения cookies
    session = requests.Session()
    
    try:
        # 1. Проверяем доступность страниц
        print("\n1️⃣ Проверка доступности страниц...")
        
        # Главная страница админки
        response = requests.get(f"{BASE_URL}/admin", timeout=5)
        print(f"   Админка: {response.status_code}")
        
        # Страница заказов магазина
        response = requests.get(f"{BASE_URL}/shop/admin/orders", timeout=5)
        print(f"   Заказы магазина: {response.status_code}")
        
        # 2. Проверяем каталог магазина
        print("\n2️⃣ Проверка каталога магазина...")
        response = session.get(f"{BASE_URL}/shop", timeout=5)
        print(f"   Каталог: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"   Длина HTML: {len(content)}")
            print(f"   Товары найдены: {'product-card' in content}")
            print(f"   Фото найдены: {'img src=' in content}")
        
        # 3. Проверяем страницу товара
        print("\n3️⃣ Проверка страницы товара...")
        response = session.get(f"{BASE_URL}/shop/product/2", timeout=5)
        print(f"   Страница товара: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"   Товар '222' найден: {'222' in content}")
            print(f"   Кнопка 'Добавить в корзину' найдена: {'Добавить в корзину' in content}")
            print(f"   Фото товара найдено: {'img src=' in content}")
        
        # 4. Проверяем корзину
        print("\n4️⃣ Проверка корзины...")
        response = session.get(f"{BASE_URL}/shop/cart", timeout=5)
        print(f"   Корзина: {response.status_code}")
        
        # 5. Добавляем товар в корзину и проверяем checkout
        print("\n5️⃣ Добавление товара в корзину...")
        response = session.post(f"{BASE_URL}/shop/cart/add", 
                               data={"product_id": "2", "quantity": "1"}, 
                               timeout=5)
        print(f"   Добавление в корзину: {response.status_code}")
        
        # 6. Проверяем оформление заказа
        print("\n6️⃣ Проверка оформления заказа...")
        response = session.get(f"{BASE_URL}/shop/checkout", timeout=5)
        print(f"   Оформление заказа: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"   Поле телефона с +7: {'value=\"+7\"' in content}")
            print(f"   Поле города найдено: {'customer_city' in content}")
            print(f"   Кнопки оплаты найдены: {'payment_method_id' in content}")
            print(f"   Города в списке: {'Грозный' in content and 'Махачкала' in content}")
            print(f"   Способы оплаты: {'Наличные на складе' in content}")
        
        print("\n✅ Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
