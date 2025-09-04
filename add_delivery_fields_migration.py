#!/usr/bin/env python3
"""
Миграция для добавления полей доставки в таблицу shop_orders
"""

import sqlite3
import os

def run_migration():
    """Выполняет миграцию базы данных"""
    db_path = "app/database.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже поля доставки
        cursor.execute("PRAGMA table_info(shop_orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'delivery_option' not in columns:
            print("➕ Добавляем поле delivery_option")
            cursor.execute("ALTER TABLE shop_orders ADD COLUMN delivery_option VARCHAR(50)")
        
        if 'delivery_city_other' not in columns:
            print("➕ Добавляем поле delivery_city_other")
            cursor.execute("ALTER TABLE shop_orders ADD COLUMN delivery_city_other VARCHAR(100)")
        
        if 'delivery_cost_rub' not in columns:
            print("➕ Добавляем поле delivery_cost_rub")
            cursor.execute("ALTER TABLE shop_orders ADD COLUMN delivery_cost_rub DECIMAL(10,2)")
        
        conn.commit()
        print("✅ Миграция выполнена успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)





