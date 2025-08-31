#!/usr/bin/env python3
"""
Простой тест для отладки корзины
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def test_cart_debug():
    """Тест отладки корзины"""
    print("🔍 Тестируем отладку корзины...")
    
    # Создаем сессию
    session = requests.Session()
    
    # 1. Получаем страницу магазина
    print("1. Получаем страницу магазина...")
    response = session.get(f"{BASE_URL}/shop/")
    print(f"   Статус: {response.status_code}")
    print(f"   Cookies: {dict(session.cookies)}")
    
    # 2. Добавляем товар в корзину
    print("\n2. Добавляем товар в корзину...")
    cart_data = {
        'product_id': '1',
        'quantity': '2'
    }
    response = session.post(f"{BASE_URL}/shop/cart/add", data=cart_data, allow_redirects=False)
    print(f"   Статус: {response.status_code}")
    print(f"   Location: {response.headers.get('Location')}")
    print(f"   Cookies после добавления: {dict(session.cookies)}")
    
    # 3. Проверяем корзину
    print("\n3. Проверяем корзину...")
    response = session.get(f"{BASE_URL}/shop/cart")
    print(f"   Статус: {response.status_code}")
    print(f"   Cookies при проверке: {dict(session.cookies)}")
    
    # 4. Проверяем содержимое корзины
    soup = BeautifulSoup(response.text, 'html.parser')
    if "Корзина пуста" in response.text:
        print("   ❌ Корзина пуста")
    else:
        print("   ✅ Корзина содержит товары")
        # Ищем товары в корзине
        cart_items = soup.find_all('div', class_='cart-item')
        print(f"   Найдено товаров: {len(cart_items)}")
    
    # 5. Проверяем API корзины
    print("\n4. Проверяем API корзины...")
    response = session.get(f"{BASE_URL}/api/shop/cart/count")
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.text}")

if __name__ == "__main__":
    test_cart_debug()
