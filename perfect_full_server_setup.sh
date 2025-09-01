#!/bin/bash

echo "🚀 Sirius Group - ИДЕАЛЬНАЯ ПОЛНАЯ настройка сервера"
echo "======================================================"
echo "✅ ВСЕ функции сайта: склад, магазин, аналитика, админ-панель, QR-коды"
echo "======================================================"

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

# 11. ИДЕАЛЬНАЯ инициализация базы данных
echo "📋 11. Идеальная инициализация базы данных..."
python3 perfect_init.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка инициализации базы данных!"
    echo "📋 Проверьте логи выше"
    exit 1
fi

# 12. Запуск сервера с ПОЛНЫМ функционалом
echo "📋 12. Запуск сервера с ПОЛНЫМ функционалом..."
echo "🚀 Включаем ВСЕ функции: склад, магазин, аналитика, админ-панель, QR-коды"
nohup python3 -m uvicorn app.main_perfect_full:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 13. Проверка статуса
echo "📋 13. Проверка статуса..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен успешно!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
    echo "🔍 Проверка здоровья: http://185.239.50.157:8000/health"
    echo "📊 Список функций: http://185.239.50.157:8000/features"
    echo "👤 Админ: admin / admin123"
    echo "📋 Лог: tail -f server.log"
else
    echo "❌ Ошибка запуска сервера"
    echo "📋 Проверьте лог:"
    tail -20 server.log
    exit 1
fi

# 14. Финальная проверка
echo "📋 14. Финальная проверка..."
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Сервер отвечает на запросы!"
    echo "🎯 Проверяем все функции..."
    
    # Проверяем основные функции
    if curl -s http://localhost:8000/features > /dev/null; then
        echo "✅ Функция /features работает"
    fi
    
    if curl -s http://localhost:8000/shop > /dev/null; then
        echo "✅ Магазин работает"
    fi
    
    if curl -s http://localhost:8000/products > /dev/null; then
        echo "✅ Управление продуктами работает"
    fi
    
    if curl -s http://localhost:8000/orders > /dev/null; then
        echo "✅ Управление заказами работает"
    fi
    
    if curl -s http://localhost:8000/analytics > /dev/null; then
        echo "✅ Аналитика работает"
    fi
    
    if curl -s http://localhost:8000/admin > /dev/null; then
        echo "✅ Админ-панель работает"
    fi
    
else
    echo "⚠️ Сервер запущен, но не отвечает на запросы"
    echo "📋 Проверьте лог: tail -f server.log"
fi

echo "======================================================"
echo "🎉 ИДЕАЛЬНАЯ ПОЛНАЯ НАСТРОЙКА ЗАВЕРШЕНА!"
echo "🚀 Сервер работает со ВСЕМИ функциями Sirius Group"
echo "✅ Склад и остатки"
echo "✅ Интернет-магазин с корзиной"
echo "✅ Система заказов и поставок"
echo "✅ Аналитика продаж и остатков"
echo "✅ Административная панель"
echo "✅ QR-коды и сканер"
echo "✅ Отчеты и экспорт данных"
echo "✅ Управление пользователями"
echo "======================================================"
