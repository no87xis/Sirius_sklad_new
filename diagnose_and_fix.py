#!/usr/bin/env python3
"""
Скрипт диагностики и исправления проблем Sirius Group
Проверяет основные компоненты и исправляет ошибки
"""

import os
import sys
import sqlite3
from pathlib import Path

def print_status(message, status="INFO"):
    """Выводит статус с цветами"""
    colors = {
        "INFO": "\033[94m",    # Синий
        "SUCCESS": "\033[92m", # Зеленый
        "WARNING": "\033[93m", # Желтый
        "ERROR": "\033[91m",   # Красный
        "RESET": "\033[0m"     # Сброс
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")

def check_database():
    """Проверяет базу данных"""
    print_status("Проверяю базу данных...", "INFO")
    
    db_path = Path("app/database/sirius.db")
    
    if not db_path.exists():
        print_status("База данных не найдена!", "ERROR")
        print_status("Создаю базу данных...", "INFO")
        
        # Создаем директорию если её нет
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Создаем пустую базу данных
            conn = sqlite3.connect(db_path)
            conn.close()
            print_status("База данных создана", "SUCCESS")
        except Exception as e:
            print_status(f"Ошибка создания БД: {e}", "ERROR")
            return False
    else:
        print_status("База данных найдена", "SUCCESS")
    
    return True

def check_imports():
    """Проверяет импорты основных модулей"""
    print_status("Проверяю импорты...", "INFO")
    
    try:
        # Проверяем основные импорты
        import app.config
        print_status("✓ app.config", "SUCCESS")
        
        import app.db
        print_status("✓ app.db", "SUCCESS")
        
        import app.models.order
        print_status("✓ app.models.order", "SUCCESS")
        
        import app.constants.delivery
        print_status("✓ app.constants.delivery", "SUCCESS")
        
        print_status("Все импорты работают", "SUCCESS")
        return True
        
    except ImportError as e:
        print_status(f"Ошибка импорта: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Неожиданная ошибка: {e}", "ERROR")
        return False

def run_delivery_migration():
    """Запускает миграцию доставки"""
    print_status("Запускаю миграцию доставки...", "INFO")
    
    try:
        # Импортируем и запускаем миграцию
        from migrations.add_delivery_system import migrate
        
        if migrate():
            print_status("Миграция доставки успешна", "SUCCESS")
            return True
        else:
            print_status("Миграция доставки не удалась", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Ошибка миграции: {e}", "ERROR")
        return False

def check_file_structure():
    """Проверяет структуру файлов"""
    print_status("Проверяю структуру файлов...", "INFO")
    
    required_files = [
        "app/main.py",
        "app/config.py",
        "app/db.py",
        "app/models/order.py",
        "app/constants/delivery.py",
        "app/schemas/shop_order.py",
        "app/templates/shop/checkout.html",
        "app/templates/shop/delivery_payment.html",
        "app/routers/delivery_payment.py",
        "migrations/add_delivery_system.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_status(f"✓ {file_path}", "SUCCESS")
        else:
            print_status(f"✗ {file_path}", "ERROR")
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"Отсутствуют файлы: {len(missing_files)}", "WARNING")
        return False
    else:
        print_status("Все файлы на месте", "SUCCESS")
        return True

def main():
    """Основная функция"""
    print_status("🚀 Начинаю диагностику Sirius Group", "INFO")
    print_status("=" * 50, "INFO")
    
    # Проверяем структуру файлов
    if not check_file_structure():
        print_status("Проблемы с файлами, останавливаюсь", "ERROR")
        return False
    
    # Проверяем импорты
    if not check_imports():
        print_status("Проблемы с импортами, останавливаюсь", "ERROR")
        return False
    
    # Проверяем базу данных
    if not check_database():
        print_status("Проблемы с БД, останавливаюсь", "ERROR")
        return False
    
    # Запускаем миграцию
    if not run_delivery_migration():
        print_status("Проблемы с миграцией", "WARNING")
    
    print_status("=" * 50, "INFO")
    print_status("✅ Диагностика завершена", "SUCCESS")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





