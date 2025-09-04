#!/usr/bin/env python3
"""
Простой скрипт для запуска сервера без цветного вывода
"""

import uvicorn
import os
import sys

# Отключаем цветной вывод
os.environ['NO_COLOR'] = '1'
os.environ['TERM'] = 'dumb'

if __name__ == "__main__":
    print("Запуск сервера Sirius Group...")
    print("Сервер будет доступен по адресу: http://localhost:8006")
    print("Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8006,
            reload=False,
            access_log=False,
            log_level="warning"
        )
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")
        sys.exit(1)


