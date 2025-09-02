"""
Миграция: Добавление системы доставки
Добавляет поля для системы доставки в таблицу orders
Безопасная миграция с обратной совместимостью
"""

import sqlite3
import os
from pathlib import Path

def migrate():
    """Выполняет миграцию для добавления системы доставки"""
    
    # Путь к базе данных
    db_path = Path("app/database/sirius.db")
    
    if not db_path.exists():
        print("❌ База данных не найдена. Создайте её сначала.")
        return False
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Начинаю миграцию системы доставки...")
        
        # Проверяем, есть ли уже поля доставки
        cursor.execute("PRAGMA table_info(orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Список полей для добавления
        delivery_fields = [
            ("delivery_option", "TEXT"),
            ("delivery_city_other", "TEXT"), 
            ("delivery_unit_price_rub", "INTEGER DEFAULT 300"),
            ("delivery_units", "INTEGER"),
            ("delivery_cost_rub", "INTEGER"),
            ("delivery_payment_enabled", "BOOLEAN DEFAULT FALSE")
        ]
        
        added_fields = []
        
        for field_name, field_type in delivery_fields:
            if field_name not in columns:
                # Добавляем поле
                sql = f"ALTER TABLE orders ADD COLUMN {field_name} {field_type}"
                cursor.execute(sql)
                added_fields.append(field_name)
                print(f"✅ Добавлено поле: {field_name}")
            else:
                print(f"ℹ️ Поле {field_name} уже существует")
        
        # Создаем индекс для быстрого поиска по типу доставки
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_delivery_option ON orders(delivery_option)")
            print("✅ Создан индекс для поля delivery_option")
        except Exception as e:
            print(f"ℹ️ Индекс уже существует: {e}")
        
        # Коммитим изменения
        conn.commit()
        
        if added_fields:
            print(f"\n🎉 Миграция завершена успешно!")
            print(f"Добавлено полей: {len(added_fields)}")
            print(f"Поля: {', '.join(added_fields)}")
        else:
            print("\nℹ️ Все поля доставки уже существуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def rollback():
    """Откатывает миграцию (удаляет поля доставки)"""
    
    db_path = Path("app/database/sirius.db")
    
    if not db_path.exists():
        print("❌ База данных не найдена")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Откатываю миграцию системы доставки...")
        
        # Получаем список полей доставки
        cursor.execute("PRAGMA table_info(orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        delivery_fields = [
            "delivery_option", "delivery_city_other", "delivery_unit_price_rub",
            "delivery_units", "delivery_cost_rub", "delivery_payment_enabled"
        ]
        
        # Создаем новую таблицу без полей доставки
        cursor.execute("""
            CREATE TABLE orders_new AS 
            SELECT id, phone, customer_name, client_city, product_id, product_name, 
                   qty, unit_price_rub, eur_rate, order_code, order_code_last4,
                   payment_method_id, payment_instrument_id, paid_amount, paid_at,
                   payment_method, payment_note, status, created_at, issued_at, user_id, source
            FROM orders
        """)
        
        # Удаляем старую таблицу и переименовываем новую
        cursor.execute("DROP TABLE orders")
        cursor.execute("ALTER TABLE orders_new RENAME TO orders")
        
        # Восстанавливаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
        
        conn.commit()
        print("✅ Откат миграции завершен успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отката: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback()
    else:
        success = migrate()
    
    sys.exit(0 if success else 1)
