#!/usr/bin/env python3
"""
Простая проверка работы сервера
"""
import requests
import time
import sys

def check_server():
    url = "http://127.0.0.1:8000"
    
    print("Проверяем сервер...")
    
    try:
        # Пробуем подключиться
        response = requests.get(url, timeout=5)
        print(f"✓ Сервер работает! Статус: {response.status_code}")
        print(f"✓ URL: {url}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не отвечает")
        print("   Возможные причины:")
        print("   1. Сервер не запущен")
        print("   2. Неправильный порт")
        print("   3. Блокировка файрволом")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Сервер не отвечает (таймаут)")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if check_server():
        print("\n🎉 Сервер работает нормально!")
        sys.exit(0)
    else:
        print("\n💥 Сервер не работает!")
        sys.exit(1)
