#!/bin/bash

echo "🔧 Sirius Group - Исправление сервера"
echo "===================================="

# 1. Остановка всех процессов
echo "📋 1. Остановка процессов..."
pkill -f uvicorn
pkill -f python
sleep 3

# 2. Очистка кэша nginx
echo "📋 2. Очистка кэша..."
sudo systemctl reload nginx 2>/dev/null || true
sudo rm -rf /var/cache/nginx/* 2>/dev/null || true

# 3. Переход в папку проекта
echo "📋 3. Переход в проект..."
cd ~/Sirius_sklad_new

# 4. Активация окружения
echo "📋 4. Активация окружения..."
source venv/bin/activate

# 5. Обновление зависимостей
echo "📋 5. Обновление зависимостей..."
pip install -r requirements.txt

# 6. Создание директорий
echo "📋 6. Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads

# 7. Инициализация базы данных
echo "📋 7. Инициализация БД..."
python3 -c "
from app.db import engine
from app.models import Base
from app.db import SessionLocal
from app.models import User
from app.services.auth import get_password_hash

print('Создание таблиц...')
Base.metadata.create_all(bind=engine)

print('Проверка админа...')
db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        print('Создание админа...')
        admin_user = User(
            username='admin',
            email='admin@sirius.com',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print('✅ Админ создан: admin / admin123')
    else:
        print('✅ Админ уже существует')
finally:
    db.close()
"

# 8. Применение миграций
echo "📋 8. Применение миграций..."
alembic upgrade head

# 9. Запуск сервера
echo "📋 9. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 10. Проверка статуса
echo "📋 10. Проверка статуса..."
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

echo "===================================="
echo "🎉 Исправление завершено!"
