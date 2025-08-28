#!/usr/bin/env python3
"""Тест создания товара"""
import requests
import json

def test_product_creation():
    print("🧪 ТЕСТ СОЗДАНИЯ ТОВАРА")
    print("=" * 50)
    
    # Тест 1: Проверка GET /products/new
    print("1️⃣ Тестирую GET /products/new...")
    try:
        response = requests.get("http://127.0.0.1:8000/products/new")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Страница открывается")
        else:
            print(f"   ❌ Ошибка: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")
    
    # Тест 2: Проверка POST /products
    print("\n2️⃣ Тестирую POST /products...")
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
        
        response = requests.post("http://127.0.0.1:8000/products", data=data)
        print(f"   Статус: {response.status_code}")
        print(f"   Редирект: {response.headers.get('location', 'Нет')}")
        
        if response.status_code == 302:
            print("   ✅ Редирект выполнен")
            # Проверяем куда редиректит
            location = response.headers.get('location', '')
            if 'success' in location:
                print("   ✅ Сообщение об успехе")
            elif 'error' in location:
                print(f"   ❌ Ошибка: {location}")
        else:
            print(f"   ❌ Неожиданный статус: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")
    
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_product_creation()
