#!/bin/bash

# Скрипт быстрого развертывания Sirius Group
echo "🚀 Начинаем развертывание Sirius Group..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Создаем виртуальное окружение
echo "📦 Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "⚙️ Создаем .env файл..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=app/static/uploads
MAX_FILE_SIZE=10485760
EOF
    echo "⚠️ ВНИМАНИЕ: Измените SECRET_KEY в .env файле!"
fi

# Создаем папки для загрузок
echo "📁 Создаем папки..."
mkdir -p app/static/uploads
mkdir -p logs

# Применяем миграции
echo "🗄️ Применяем миграции базы данных..."
alembic upgrade head

# Создаем .gitkeep для uploads
touch app/static/uploads/.gitkeep

echo "✅ Развертывание завершено!"
echo "🚀 Запуск сервера:"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Доступные страницы:"
echo "   - Админка: http://localhost:8000/"
echo "   - Магазин: http://localhost:8000/shop"
echo "   - API docs: http://localhost:8000/docs"
