#!/usr/bin/env python3
"""
Простой тестовый скрипт для диагностики сервера
"""
import sys
import traceback
import uvicorn
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("=== ДИАГНОСТИКА СЕРВЕРА ===")
    print("1. Проверяем Python...")
    print(f"   Python version: {sys.version}")
    
    print("\n2. Проверяем импорты...")
    import fastapi
    print(f"   FastAPI: {fastapi.__version__}")
    
    import uvicorn
    print(f"   Uvicorn: {uvicorn.__version__}")
    
    print("\n3. Импортируем приложение...")
    from app.main import app
    print("   ✓ Приложение импортировано")
    
    print("\n4. Проверяем роутеры...")
    print(f"   Количество роутеров: {len(app.routes)}")
    
    print("\n5. Запускаем сервер...")
    print("   Сервер запускается на http://127.0.0.1:8000")
    print("   Для остановки нажмите Ctrl+C")
    print("   " + "="*50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    print("\nДетали ошибки:")
    traceback.print_exc()
    sys.exit(1)
