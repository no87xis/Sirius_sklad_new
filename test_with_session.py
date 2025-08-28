#!/usr/bin/env python3
"""Тест с сессией для имитации браузера"""
import requests

def test_with_session():
    print("🧪 ТЕСТ С СЕССИЕЙ (имитация браузера)")
    print("=" * 50)
    
    # Создаем сессию
    session = requests.Session()
    
    # Шаг 1: Логин
    print("1️⃣ Логин...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = session.post("http://127.0.0.1:8000/login", data=login_data)
        print(f"   Статус логина: {response.status_code}")
        print(f"   Редирект: {response.headers.get('location', 'Нет')}")
        
        if response.status_code == 302:
            print("   ✅ Логин успешен")
        else:
            print(f"   ❌ Ошибка логина: {response.text[:200]}")
            return
            
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")
        return
    
    # Шаг 2: Проверка страницы создания товара
    print("\n2️⃣ Проверка GET /products/new...")
    try:
        response = session.get("http://127.0.0.1:8000/products/new")
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Страница открывается")
            # Проверяем, что action="/products" в HTML
            if 'action="/products"' in response.text:
                print("   ✅ action='/products' найден в HTML")
            else:
                print("   ❌ action='/products' НЕ найден в HTML")
                print("   HTML содержит:", response.text[response.text.find('<form'):response.text.find('<form')+200])
        else:
            print(f"   ❌ Ошибка: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")
    
    # Шаг 3: Тест создания товара
    print("\n3️⃣ Тест POST /products...")
    try:
        data = {
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'min_stock': 5,
            'buy_price_eur': 10.50,
            'sell_price_rub': 1500.00,
            'supplier_name': 'Тестовый поставщик',
            'initial_quantity': 20
        }
        
        response = session.post("http://127.0.0.1:8000/products", data=data)
        print(f"   Статус: {response.status_code}")
        print(f"   Редирект: {response.headers.get('location', 'Нет')}")
        
        if response.status_code == 302:
            location = response.headers.get('location', '')
            if 'success' in location:
                print("   ✅ Товар создан успешно")
            elif 'error' in location:
                print(f"   ❌ Ошибка создания: {location}")
            else:
                print(f"   ⚠️ Неожиданный редирект: {location}")
        else:
            print(f"   ❌ Неожиданный статус: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")
    
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_with_session()
