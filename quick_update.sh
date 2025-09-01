#!/bin/bash

echo "⚡ Sirius Group - Быстрое обновление"
echo "==================================="

# 1. Остановка сервера
echo "📋 1. Остановка сервера..."
pkill -f uvicorn
sleep 2

# 2. Обновление кода
echo "📋 2. Обновление кода..."
git stash
git pull origin master

# 3. Активация окружения
echo "📋 3. Активация окружения..."
source venv/bin/activate

# 4. Обновление зависимостей
echo "📋 4. Обновление зависимостей..."
pip install -r requirements.txt

# 5. Применение миграций
echo "📋 5. Применение миграций..."
alembic upgrade head

# 6. Запуск сервера
echo "📋 6. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 7. Проверка
echo "📋 7. Проверка статуса..."
sleep 3
if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Обновление завершено успешно!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
else
    echo "❌ Ошибка запуска"
    echo "📋 Лог: tail -f server.log"
fi

echo "==================================="
