#!/bin/bash

echo "🚀 Sirius Group - Правильная настройка сервера"
echo "=============================================="

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

# 11. Правильная инициализация базы данных
echo "📋 11. Инициализация базы данных..."
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from app.db import engine
from app.models import Base
from app.db import SessionLocal
from app.models import User, UserRole
from app.services.auth import get_password_hash

print('Создание таблиц...')
Base.metadata.create_all(bind=engine)

print('Создание админа...')
db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.ADMIN,
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

print('✅ База данных инициализирована!')
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

echo "=============================================="
echo "🎉 Настройка завершена!"
