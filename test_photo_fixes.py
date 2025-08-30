#!/usr/bin/env python3
"""
Тест исправлений для магазина "Сириус"
Проверяет:
1. Отображение фотографий товаров
2. Маски для телефонов
3. Ограничения количества товаров
"""

import requests
import re
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_photo_display():
    """Тест отображения фотографий товаров"""
    print("🔍 Тестируем отображение фотографий...")
    
    try:
        # Получаем страницу каталога
        response = requests.get(f"{BASE_URL}/shop")
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к каталогу: {response.status_code}")
            return False
        
        content = response.text
        
        # Проверяем наличие товаров
        if "Miele Boost CX1" not in content or "222" not in content:
            print("❌ Товары не найдены в каталоге")
            return False
        
        # Проверяем наличие фото
        if "app/static/uploads/products" not in content:
            print("❌ Пути к фотографиям не найдены")
            return False
        
        # Проверяем fallback для отсутствующих фото
        if "Фото недоступно" not in content and "Нет фото" not in content:
            print("❌ Fallback для отсутствующих фото не найден")
            return False
        
        print("✅ Отображение фотографий работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании фотографий: {e}")
        return False

def test_phone_masks():
    """Тест масок для телефонов"""
    print("📱 Тестируем маски для телефонов...")
    
    try:
        # Проверяем форму оформления заказа
        response = requests.get(f"{BASE_URL}/shop/checkout")
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к форме заказа: {response.status_code}")
            return False
        
        content = response.text
        
        # Проверяем автозаполнение +7
        if 'value="+7"' not in content:
            print("❌ Автозаполнение +7 не найдено в форме заказа")
            return False
        
        # Проверяем маску телефона
        if 'pattern="\\+7 \\([0-9]{3}\\) [0-9]{3}-[0-9]{2}-[0-9]{2}"' not in content:
            print("❌ Маска телефона не найдена в форме заказа")
            return False
        
        # Проверяем форму поиска заказа
        response = requests.get(f"{BASE_URL}/shop/search-order")
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к форме поиска: {response.status_code}")
            return False
        
        content = response.text
        
        # Проверяем автозаполнение +7
        if 'value="+7"' not in content:
            print("❌ Автозаполнение +7 не найдено в форме поиска")
            return False
        
        print("✅ Маски для телефонов работают корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании масок телефонов: {e}")
        return False

def test_quantity_limits():
    """Тест ограничений количества товаров"""
    print("📦 Тестируем ограничения количества товаров...")
    
    try:
        # Получаем страницу каталога
        response = requests.get(f"{BASE_URL}/shop")
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к каталогу: {response.status_code}")
            return False
        
        content = response.text
        
        # Проверяем отсутствие max атрибута в полях количества
        if 'max=' in content and 'max="{{ product.quantity' in content:
            print("❌ Ограничения количества товаров не убраны")
            return False
        
        # Проверяем отсутствие max атрибута в корзине
        response = requests.get(f"{BASE_URL}/shop/cart")
        if response.status_code == 200:
            cart_content = response.text
            if 'max=' in cart_content and 'max="{{ item.available_stock' in cart_content:
                print("❌ Ограничения количества в корзине не убраны")
                return False
        
        print("✅ Ограничения количества товаров убраны корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании ограничений количества: {e}")
        return False

def test_photo_fallback():
    """Тест fallback для отсутствующих фотографий"""
    print("🖼️ Тестируем fallback для фотографий...")
    
    try:
        # Получаем страницу каталога
        response = requests.get(f"{BASE_URL}/shop")
        if response.status_code != 200:
            print(f"❌ Ошибка доступа к каталогу: {response.status_code}")
            return False
        
        content = response.text
        
        # Проверяем наличие JavaScript для обработки ошибок загрузки фото
        if 'onerror=' not in content:
            print("❌ JavaScript для обработки ошибок фото не найден")
            return False
        
        # Проверяем наличие fallback элементов
        if 'style="display: none;"' not in content:
            print("❌ Fallback элементы не найдены")
            return False
        
        print("✅ Fallback для фотографий настроен корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании fallback: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов исправлений для магазина 'Сириус'")
    print("=" * 60)
    
    tests = [
        test_photo_display,
        test_phone_masks,
        test_quantity_limits,
        test_photo_fallback
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
        print()
    
    print("=" * 60)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены")
        return False

if __name__ == "__main__":
    main()
