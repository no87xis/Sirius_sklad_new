#!/usr/bin/env python3
"""
Исправление роли админа в базе данных
"""

import sqlite3

def fix_admin_role():
    """Исправить роль админа на ADMIN"""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('sirius.db')
        cursor = conn.cursor()
        
        # Обновляем роль админа
        cursor.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'admin'")
        
        # Проверяем результат
        cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Роль админа исправлена: {result[0]} -> {result[1]}")
        else:
            print("❌ Админ не найден")
        
        # Сохраняем изменения
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fix_admin_role()
