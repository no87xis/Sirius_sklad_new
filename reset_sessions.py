#!/usr/bin/env python3
"""
Скрипт для сброса сессий и очистки кэша
"""
import os
import shutil
from pathlib import Path

def clear_cache():
    """Очистить кэш и временные файлы"""
    print("🧹 Очистка кэша...")
    
    # Удаляем файлы кэша Python
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"   ✅ Удален {cache_dir}")
    
    # Удаляем .pyc файлы
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))
                print(f"   ✅ Удален {os.path.join(root, file)}")
    
    print("✅ Кэш очищен")

def check_database():
    """Проверить базу данных"""
    print("\n📊 Проверка базы данных...")
    
    if os.path.exists("sirius.db"):
        size = os.path.getsize("sirius.db")
        print(f"   ✅ База данных существует, размер: {size} байт")
    else:
        print("   ❌ База данных не найдена")

def main():
    print("🔄 Сброс сессий и очистка кэша")
    print("=" * 50)
    
    clear_cache()
    check_database()
    
    print("\n📋 Рекомендации:")
    print("1. Перезапустите сервер: uvicorn app.main:app --reload")
    print("2. Очистите кэш браузера (Ctrl+Shift+Delete)")
    print("3. Попробуйте режим инкогнито")
    print("4. Проверьте /debug-session для диагностики")

if __name__ == "__main__":
    main()
