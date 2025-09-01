#!/usr/bin/env python3
"""
Простая диагностика сервера Sirius Group
"""

import sys
import os

def main():
    print("🔍 Sirius Group - Диагностика сервера")
    print("=" * 50)
    
    # 1. Проверяем Python
    print(f"🐍 Python версия: {sys.version}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    
    # 2. Проверяем структуру проекта
    print("\n📁 Структура проекта:")
    for item in os.listdir('.'):
        if os.path.isdir(item):
            print(f"  📁 {item}/")
        else:
            print(f"  📄 {item}")
    
    # 3. Проверяем app папку
    if os.path.exists('app'):
        print("\n📁 Содержимое app/:")
        for item in os.listdir('app'):
            if os.path.isdir(item):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    
    # 4. Проверяем main.py
    if os.path.exists('app/main.py'):
        print("\n📄 app/main.py найден")
        try:
            with open('app/main.py', 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  📏 Размер: {len(content)} символов")
                print(f"  🔍 Содержит 'FastAPI': {'FastAPI' in content}")
                print(f"  🔍 Содержит 'app.include_router': {'app.include_router' in content}")
        except Exception as e:
            print(f"  ❌ Ошибка чтения: {e}")
    else:
        print("\n❌ app/main.py НЕ НАЙДЕН!")
    
    # 5. Проверяем requirements.txt
    if os.path.exists('requirements.txt'):
        print("\n📋 requirements.txt найден")
        try:
            with open('requirements.txt', 'r') as f:
                lines = f.readlines()
                print(f"  📏 Количество зависимостей: {len(lines)}")
                for line in lines[:5]:  # Показываем первые 5
                    print(f"    {line.strip()}")
                if len(lines) > 5:
                    print(f"    ... и еще {len(lines) - 5}")
        except Exception as e:
            print(f"  ❌ Ошибка чтения: {e}")
    else:
        print("\n❌ requirements.txt НЕ НАЙДЕН!")
    
    # 6. Проверяем виртуальное окружение
    if os.path.exists('venv'):
        print("\n🐍 Виртуальное окружение найдено")
        if os.path.exists('venv/bin/python') or os.path.exists('venv/Scripts/python.exe'):
            print("  ✅ Python найден в venv")
        else:
            print("  ❌ Python НЕ найден в venv")
    else:
        print("\n❌ Виртуальное окружение НЕ НАЙДЕНО!")
    
    # 7. Пробуем импортировать основные модули
    print("\n🔧 Тест импорта модулей:")
    
    try:
        import app
        print("  ✅ import app - УСПЕШНО")
    except Exception as e:
        print(f"  ❌ import app - ОШИБКА: {e}")
    
    try:
        from app import db
        print("  ✅ from app import db - УСПЕШНО")
    except Exception as e:
        print(f"  ❌ from app import db - ОШИБКА: {e}")
    
    try:
        from app import models
        print("  ✅ from app import models - УСПЕШНО")
    except Exception as e:
        print(f"  ❌ from app import models - ОШИБКА: {e}")
    
    try:
        from app.main import app
        print("  ✅ from app.main import app - УСПЕШНО")
    except Exception as e:
        print(f"  ❌ from app.main import app - ОШИБКА: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Диагностика завершена!")
    print("📋 Теперь мы знаем, что именно не работает")

if __name__ == "__main__":
    main()
