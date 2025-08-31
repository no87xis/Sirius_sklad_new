#!/bin/bash

echo "🔧 Быстрое исправление проблем на сервере..."

# Проверяем где мы находимся
if [ ! -f "app/main.py" ]; then
    echo "❌ Не в папке проекта. Перейдите в папку Sirius_sklad_new"
    exit 1
fi

echo "📁 Текущая папка: $(pwd)"

# Останавливаем старый сервер
echo "🛑 Останавливаем старый сервер..."
pkill -f uvicorn

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активируем виртуальное окружение..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "⚙️ Создаем .env файл..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=app/static/uploads
MAX_FILE_SIZE=10485760
EOF
fi

# Создаем папки
echo "📁 Создаем папки..."
mkdir -p app/static/uploads
mkdir -p app/static/qr
mkdir -p logs

# Инициализируем базу данных
echo "🗄️ Инициализируем базу данных..."
python3 -c "
from app.db import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ База данных инициализирована')
"

# Применяем миграции
echo "🗄️ Применяем миграции..."
alembic upgrade head

echo "✅ Исправление завершено!"
echo ""
echo "🚀 Запускаем сервер..."
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""

# Запускаем сервер
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
