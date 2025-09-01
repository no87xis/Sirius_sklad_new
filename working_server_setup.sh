#!/bin/bash

echo "🚀 Sirius Group - Рабочая настройка сервера"
echo "=========================================="

# 1. Остановка всех процессов
echo "📋 1. Остановка процессов..."
pkill -f uvicorn
pkill -f python
sleep 3

# 2. Очистка кэша nginx
echo "📋 2. Очистка кэша nginx..."
sudo systemctl reload nginx 2>/dev/null || true
sudo rm -rf /var/cache/nginx/* 2>/dev/null || true

# 3. Сохранение базы данных (если есть)
echo "📋 3. Сохранение базы данных..."
if [ -f "Sirius_sklad_new/sirius_sklad.db" ]; then
    cp Sirius_sklad_new/sirius_sklad.db sirius_sklad_backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ База данных сохранена"
fi

# 4. ПОЛНАЯ ОЧИСТКА
echo "📋 4. ПОЛНАЯ ОЧИСТКА..."
rm -rf Sirius_sklad_new
echo "✅ Старая папка удалена"

# 5. Клонирование с GitHub
echo "📋 5. Клонирование с GitHub..."
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new
echo "✅ Код загружен"

# 6. Создание виртуального окружения
echo "📋 6. Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Виртуальное окружение создано"

# 7. Установка зависимостей
echo "📋 7. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# 8. Создание .env файла
echo "📋 8. Настройка конфигурации..."
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
EOF

# 9. Создание директорий
echo "📋 9. Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads

# 10. Восстановление базы данных (если была)
echo "📋 10. Восстановление базы данных..."
if [ -f "../sirius_sklad_backup_$(date +%Y%m%d)*.db" ]; then
    echo "🔄 Восстанавливаем базу данных..."
    cp ../sirius_sklad_backup_*.db sirius_sklad.db
    echo "✅ База данных восстановлена"
fi

# 11. Создание ПОЛНОЙ базы данных
echo "📋 11. Создание полной базы данных..."
python3 -c "
import sqlite3
import os

# Создаем базу данных если её нет
if not os.path.exists('sirius_sklad.db'):
    print('Создание полной базы данных...')
    conn = sqlite3.connect('sirius_sklad.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица продуктов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price_rub DECIMAL(10,2),
            stock_quantity INTEGER DEFAULT 0,
            availability_status TEXT DEFAULT 'В наличии',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            user_id TEXT,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            unit_price_rub DECIMAL(10,2),
            total_amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            payment_method TEXT DEFAULT 'unpaid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            qr_payload TEXT,
            qr_image_path TEXT,
            qr_generated_at TIMESTAMP
        )
    ''')
    
    # Таблица корзины
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица фотографий продуктов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            photo_url TEXT NOT NULL,
            is_main BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем админа (пароль: admin123)
    import hashlib
    password = 'admin123'
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, hashed_password, role, is_active, is_superuser)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', hashed, 'admin', True, True))
    
    # Создаем тестовый продукт
    cursor.execute('''
        INSERT OR IGNORE INTO products (name, description, price_rub, stock_quantity, availability_status)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Тестовый продукт', 'Описание тестового продукта', 1000.00, 100, 'В наличии'))
    
    conn.commit()
    conn.close()
    print('✅ Полная база данных создана с админом: admin / admin123')
else:
    print('✅ База данных уже существует')
"

# 12. Запуск сервера
echo "📋 12. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 13. Проверка статуса
echo "📋 13. Проверка статуса..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен успешно!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
    echo "👤 Админ: admin / admin123"
    echo "📋 Лог: tail -f server.log"
else
    echo "❌ Ошибка запуска сервера"
    echo "📋 Проверьте лог:"
    tail -20 server.log
fi

echo "=========================================="
echo "🎉 Настройка завершена!"
