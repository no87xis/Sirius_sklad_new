#!/bin/bash

echo "🚀 Sirius Group - Полное обновление сервера"
echo "=========================================="

# 1. Остановка всех процессов
echo "📋 1. Остановка сервера..."
pkill -f uvicorn
pkill -f python
sleep 2

# 2. Очистка nginx кэша
echo "📋 2. Очистка кэша..."
sudo systemctl reload nginx
sudo rm -rf /var/cache/nginx/*

# 3. Сохранение базы данных (если есть)
echo "📋 3. Сохранение данных..."
if [ -f "sirius_sklad.db" ]; then
    cp sirius_sklad.db sirius_sklad_backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ База данных сохранена"
fi

# 4. Полная очистка и переустановка
echo "📋 4. Полная переустановка..."
cd ~
rm -rf Sirius_sklad_new
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new

# 5. Создание виртуального окружения
echo "📋 5. Создание окружения..."
python3 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
echo "📋 6. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Создание .env файла
echo "📋 7. Настройка конфигурации..."
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
EOF

# 8. Создание директорий
echo "📋 8. Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads

# 9. Инициализация базы данных
echo "📋 9. Инициализация базы данных..."
python3 -c "
from app.db import engine
from app.models import Base
from app.db import SessionLocal
from app.models import User
from app.services.auth import get_password_hash

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

# Создаем админа
db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
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

# 10. Применение миграций
echo "📋 10. Применение миграций..."
alembic upgrade head

# 11. Восстановление базы данных (если нужно)
echo "📋 11. Восстановление данных..."
if [ -f "../sirius_sklad_backup_$(date +%Y%m%d)*.db" ]; then
    echo "⚠️  Найдена резервная копия. Восстановить? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cp ../sirius_sklad_backup_*.db sirius_sklad.db
        echo "✅ База данных восстановлена"
    fi
fi

# 12. Запуск сервера
echo "📋 12. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 13. Проверка статуса
echo "📋 13. Проверка статуса..."
sleep 5
if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен успешно!"
    echo "🌐 Сайт доступен по адресу: http://185.239.50.157:8000"
    echo "👤 Админ: admin / admin123"
else
    echo "❌ Ошибка запуска сервера"
    echo "📋 Проверьте лог: tail -f server.log"
fi

echo "=========================================="
echo "🎉 Обновление завершено!"
