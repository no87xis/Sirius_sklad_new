#!/bin/bash

echo "🧹 Sirius Group - Полная очистка и обновление"
echo "============================================="

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
cd ~
if [ -f "Sirius_sklad_new/sirius_sklad.db" ]; then
    cp Sirius_sklad_new/sirius_sklad.db sirius_sklad_backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ База данных сохранена"
fi

# 4. ПОЛНАЯ ОЧИСТКА - удаление старой папки
echo "📋 4. ПОЛНАЯ ОЧИСТКА..."
echo "⚠️  УДАЛЯЕМ старую папку полностью!"
rm -rf Sirius_sklad_new
echo "✅ Старая папка удалена"

# 5. Очистка виртуального окружения (если есть)
echo "📋 5. Очистка виртуального окружения..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ Старое виртуальное окружение удалено"
fi

# 6. Очистка кэша pip
echo "📋 6. Очистка кэша pip..."
pip cache purge 2>/dev/null || true
echo "✅ Кэш pip очищен"

# 7. Клонирование заново с GitHub
echo "📋 7. Клонирование с GitHub..."
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new
echo "✅ Код загружен заново"

# 8. Создание нового виртуального окружения
echo "📋 8. Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Виртуальное окружение создано"

# 9. Установка зависимостей
echo "📋 9. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# 10. Создание .env файла
echo "📋 10. Настройка конфигурации..."
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
EOF

# 11. Создание директорий
echo "📋 11. Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads

# 12. Восстановление базы данных (если была)
echo "📋 12. Восстановление базы данных..."
if [ -f "../sirius_sklad_backup_$(date +%Y%m%d)*.db" ]; then
    echo "🔄 Восстанавливаем базу данных..."
    cp ../sirius_sklad_backup_*.db sirius_sklad.db
    echo "✅ База данных восстановлена"
else
    echo "📝 Создаем новую базу данных..."
fi

# 13. Инициализация базы данных
echo "📋 13. Инициализация базы данных..."
python3 -c "
from app.db import engine
from app.models import Base
from app.db import SessionLocal
from app.models import User
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

# 14. Применение миграций
echo "📋 14. Применение миграций..."
alembic upgrade head

# 15. Запуск сервера
echo "📋 15. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 16. Проверка статуса
echo "📋 16. Проверка статуса..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен успешно!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
    echo "👤 Админ: admin / admin123"
    echo "📋 Лог: tail -f server.log"
    
    # Показываем информацию о версии
    echo "📊 Информация о версии:"
    echo "Коммит: $(git rev-parse --short HEAD)"
    echo "Дата: $(git log -1 --format=%cd)"
    echo "Автор: $(git log -1 --format=%an)"
    echo "Сообщение: $(git log -1 --format=%s)"
else
    echo "❌ Ошибка запуска сервера"
    echo "📋 Проверьте лог:"
    tail -20 server.log
fi

echo "============================================="
echo "🎉 ПОЛНАЯ ОЧИСТКА И ОБНОВЛЕНИЕ ЗАВЕРШЕНЫ!"
echo "🧹 Старое удалено, новое установлено!"
