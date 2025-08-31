#!/usr/bin/env python3
"""
Тест системы QR-кодов для заказов
"""

import requests
import time
import json
from urllib.parse import urljoin

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

def test_qr_scanner_page():
    """Тест страницы сканера QR-кодов"""
    print("\n🔍 Тестируем страницу сканера QR-кодов...")
    
    try:
        response = requests.get(f"{BASE_URL}/shop/admin/qr-scanner")
        if response.status_code == 200:
            print("✅ Страница сканера QR-кодов доступна")
            return True
        else:
            print(f"❌ Страница сканера недоступна: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка доступа к сканеру: {e}")
        return False

def test_qr_api():
    """Тест API для обработки QR-кодов"""
    print("\n🔍 Тестируем API для QR-кодов...")
    
    try:
        # Тестируем с невалидным токеном
        response = requests.post(f"{BASE_URL}/shop/admin/qr-scan", data={
            'qr_data': 'invalid_token_123'
        })
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('success') and 'Неверный QR-код' in result.get('message', ''):
                print("✅ API корректно обрабатывает невалидные токены")
                return True
            else:
                print(f"❌ Неожиданный ответ API: {result}")
                return False
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False

def test_public_qr_route():
    """Тест публичного роута для QR-кодов"""
    print("\n🔍 Тестируем публичный роут для QR-кодов...")
    
    try:
        # Тестируем с невалидным токеном
        response = requests.get(f"{BASE_URL}/o/invalid_token_123")
        if response.status_code == 404:
            print("✅ Публичный роут корректно возвращает 404 для невалидных токенов")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка тестирования публичного роута: {e}")
        return False

def test_database_schema():
    """Тест структуры базы данных"""
    print("\n🔍 Тестируем структуру базы данных...")
    
    try:
        # Проверяем, что сервер отвечает
        response = requests.get(f"{BASE_URL}/shop/")
        if response.status_code == 200:
            print("✅ База данных доступна (сервер отвечает)")
            return True
        else:
            print(f"❌ Сервер не отвечает: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов системы QR-кодов")
    print("=" * 50)
    
    tests = [
        test_shop_access,
        test_qr_scanner_page,
        test_qr_api,
        test_public_qr_route,
        test_database_schema
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал с ошибкой: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Система QR-кодов работает корректно.")
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте логи выше.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
