#!/usr/bin/env python3
"""Простой тест сервера"""
import requests
import time

def test_server():
    print("🧪 ПРОСТОЙ ТЕСТ СЕРВЕРА")
    print("=" * 50)
    
    # Ждем запуска сервера
    print("⏳ Ждем запуска сервера...")
    time.sleep(3)
    
    # Тест 1: Проверка доступности
    print("\n1️⃣ Проверка доступности сервера...")
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Сервер отвечает")
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Сервер не доступен")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Проверка логина
    print("\n2️⃣ Проверка логина...")
    try:
        session = requests.Session()
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = session.post("http://127.0.0.1:8000/login", data=login_data, timeout=5)
        print(f"   Статус логина: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Логин успешен")
            
            # Тест 3: Проверка создания товара
            print("\n3️⃣ Тест создания товара...")
            try:
                data = {
                    'name': 'Тестовый товар',
                    'description': 'Описание тестового товара',
                    'min_stock': 5,
                    'buy_price_eur': '10.50',
                    'sell_price_rub': '1500.00',
                    'supplier_name': 'Тестовый поставщик',
                    'initial_quantity': 20
                }
                
                response = session.post("http://127.0.0.1:8000/products", data=data, timeout=5)
                print(f"   Статус создания: {response.status_code}")
                print(f"   Редирект: {response.headers.get('location', 'Нет')}")
                
                if response.status_code == 302:
                    location = response.headers.get('location', '')
                    if 'success' in location:
                        print("   ✅ Товар создан успешно!")
                    else:
                        print(f"   ⚠️ Неожиданный редирект: {location}")
                else:
                    print(f"   ❌ Ошибка создания: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка создания товара: {e}")
        else:
            print(f"   ❌ Ошибка логина: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка теста: {e}")
    
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_server()
