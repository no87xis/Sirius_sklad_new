#!/usr/bin/env python3
"""Быстрый тест фотографий"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def main():
    try:
        print("🔍 Проверяем каталог...")
        response = requests.get(f"{BASE_URL}/shop", timeout=5)
        print(f"Статус каталога: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Длина HTML: {len(content)}")
            print(f"Товар '222' найден: {'222' in content}")
            print(f"Товар 'Miele' найден: {'Miele' in content}")
            print(f"Фото найдены: {'app/static/uploads/products' in content}")
            print(f"Количество упоминаний 'product-card': {content.count('product-card')}")
            
            # Проверим конкретную страницу товара
            print("\n🔍 Проверяем страницу товара...")
            response2 = requests.get(f"{BASE_URL}/shop/product/2", timeout=5)
            print(f"Статус страницы товара: {response2.status_code}")
            
            if response2.status_code == 200:
                content2 = response2.text
                print(f"Фото на странице товара: {'app/static/uploads/products' in content2}")
                print(f"Товар '222' на странице: {'222' in content2}")
        
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
