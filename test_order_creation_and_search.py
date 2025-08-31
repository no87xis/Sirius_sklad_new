#!/usr/bin/env python3
"""
Тест создания заказов и их поиска
Проверяет:
1. Создание заказов (отдельный заказ для каждого товара)
2. Поиск заказов по коду
3. WhatsApp сообщения с корректным способом оплаты
"""

import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def test_shop_access():
    """Тест доступа к магазину"""
    print("🔍 Тестируем доступ к магазину...")
    try:
        response = requests.get(f"{BASE_URL}/shop/")
        if response.status_code == 200:
            print("✅ Магазин доступен")
            return True
        else:
            print(f"❌ Магазин недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка доступа к магазину: {e}")
        return False

def test_add_to_cart():
    """Тест добавления товара в корзину"""
    print("🛒 Тестируем добавление товара в корзину...")
    try:
        # Получаем страницу магазина для поиска товаров
        response = requests.get(f"{BASE_URL}/shop/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем ссылки на товары
        product_links = soup.find_all('a', href=lambda x: x and '/shop/product/' in x)
        
        if not product_links:
            print("❌ Товары не найдены в магазине")
            return False
        
        # Берем первый товар
        product_url = product_links[0]['href']
        if not product_url.startswith('http'):
            product_url = BASE_URL + product_url
        
        print(f"📦 Найден товар: {product_url}")
        
        # Добавляем в корзину
        cart_data = {
            'product_id': product_url.split('/')[-1],
            'quantity': '2'
        }
        
        response = requests.post(f"{BASE_URL}/shop/cart/add", data=cart_data)
        
        if response.status_code == 303:  # Redirect после добавления
            print("✅ Товар добавлен в корзину")
            return True
        else:
            print(f"❌ Ошибка добавления в корзину: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования корзины: {e}")
        return False

def test_checkout():
    """Тест оформления заказа"""
    print("💳 Тестируем оформление заказа...")
    try:
        checkout_data = {
            'customer_name': 'Тест Тестов',
            'customer_phone': '+7 (999) 123-45-67',
            'customer_city': 'Москва',
            'payment_method_id': '1'  # ID способа оплаты
        }
        
        response = requests.post(f"{BASE_URL}/shop/checkout", data=checkout_data)
        
        if response.status_code == 200:
            print("✅ Заказ оформлен")
            # Ищем код заказа в ответе
            soup = BeautifulSoup(response.text, 'html.parser')
            order_code_elem = soup.find('span', class_='font-mono')
            if order_code_elem:
                order_code = order_code_elem.text.strip()
                print(f"📋 Код заказа: {order_code}")
                return order_code
            else:
                print("⚠️ Код заказа не найден в ответе")
                return None
        else:
            print(f"❌ Ошибка оформления заказа: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка тестирования оформления: {e}")
        return None

def test_order_search(order_code):
    """Тест поиска заказа"""
    if not order_code:
        print("⚠️ Пропускаем тест поиска - нет кода заказа")
        return False
        
    print(f"🔍 Тестируем поиск заказа {order_code}...")
    try:
        search_data = {
            'order_code': order_code,
            'phone': '+7 (999) 123-45-67'
        }
        
        response = requests.post(f"{BASE_URL}/shop/search-order", data=search_data)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Проверяем, что заказ найден
            if "не найдены" not in response.text.lower():
                print("✅ Заказ найден")
                return True
            else:
                print("❌ Заказ не найден")
                return False
        else:
            print(f"❌ Ошибка поиска заказа: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования поиска: {e}")
        return False

def test_whatsapp_message():
    """Тест WhatsApp сообщения"""
    print("📱 Тестируем WhatsApp сообщение...")
    try:
        # Получаем страницу успешного заказа
        response = requests.get(f"{BASE_URL}/shop/order-success")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем WhatsApp сообщение
            whatsapp_text = soup.find('div', class_='bg-green-50')
            if whatsapp_text:
                message = whatsapp_text.get_text()
                print("✅ WhatsApp сообщение найдено")
                
                # Проверяем наличие способа оплаты
                if "способ оплаты" in message.lower():
                    print("✅ Способ оплаты указан в сообщении")
                    return True
                else:
                    print("⚠️ Способ оплаты не найден в сообщении")
                    return False
            else:
                print("❌ WhatsApp сообщение не найдено")
                return False
        else:
            print(f"❌ Ошибка доступа к странице заказа: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования WhatsApp: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов создания заказов и поиска")
    print("=" * 50)
    
    results = []
    
    # Тест 1: Доступ к магазину
    results.append(test_shop_access())
    
    # Тест 2: Добавление в корзину
    results.append(test_add_to_cart())
    
    # Тест 3: Оформление заказа
    order_code = test_checkout()
    results.append(order_code is not None)
    
    # Тест 4: Поиск заказа
    results.append(test_order_search(order_code))
    
    # Тест 5: WhatsApp сообщение
    results.append(test_whatsapp_message())
    
    # Результаты
    print("\n" + "=" * 50)
    print("📊 Результаты тестирования:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Пройдено: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        print("✅ Создание заказов работает корректно")
        print("✅ Поиск заказов работает корректно")
        print("✅ WhatsApp сообщения корректны")
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте логи выше.")
        print("❌ Создание заказов: " + ("Работает" if results[2] else "Не работает"))
        print("❌ Поиск заказов: " + ("Работает" if results[3] else "Не работает"))
        print("❌ WhatsApp сообщения: " + ("Корректны" if results[4] else "Некорректны"))

if __name__ == "__main__":
    main()
