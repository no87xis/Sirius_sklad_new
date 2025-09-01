#!/bin/bash

echo "🚀 Sirius Group - Быстрое исправление базы данных"
echo "=================================================="

# Переходим в папку проекта
cd Sirius_sklad_new

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем исправленный скрипт инициализации
echo "🔧 Запускаем исправленную инициализацию..."
python3 fix_init.py

if [ $? -eq 0 ]; then
    echo "✅ База данных исправлена!"
    echo "🚀 Запускаем сервер..."
    
    # Запускаем сервер
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
    
    # Проверяем статус
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
else
    echo "❌ Ошибка исправления базы данных"
fi
