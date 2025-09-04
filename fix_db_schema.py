#!/usr/bin/env python3
"""
Исправление схемы базы данных
"""

import sqlite3
import os

def fix_db_schema():
    """Добавить недостающие колонки в таблицу users"""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('sirius.db')
        cursor = conn.cursor()
        
        # Проверяем существующие колонки
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Существующие колонки: {columns}")
        
        # Добавляем недостающие колонки
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("✅ Добавлена колонка is_active")
        
        if 'is_superuser' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT 0")
            print("✅ Добавлена колонка is_superuser")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Добавлена колонка created_at")
        
        # Сохраняем изменения
        conn.commit()
        
        # Создаем админа
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        
        # Хешированный пароль для admin123
        hashed_password = '$2b$12$1DWIGB9tVddrICjPbQyL7eiB7G6Vezoy/56VqowQbTQbEe5uC7iZK'
        
        cursor.execute("""
            INSERT INTO users (username, hashed_password, role, is_active, is_superuser) 
            VALUES (?, ?, ?, ?, ?)
        """, ('admin', hashed_password, 'admin', 1, 1))
        
        conn.commit()
        print("✅ Админ создан: admin / admin123")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_db_schema()
