#!/bin/bash

echo "🚀 Начинаем развертывание Sirius Group..."

# Создаем виртуальное окружение
echo "📦 Создаем виртуальное окружение..."
python -m venv venv
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
echo "📥 Устанавливаем зависимости..."
pip install -r requirements.txt

# Дополнительные зависимости
echo "📦 Устанавливаем дополнительные зависимости..."
pip install pydantic-settings itsdangerous qrcode pillow

# Создаем .env файл если его нет
echo "⚙️ Создаем .env файл..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Настройки базы данных
DATABASE_URL=sqlite:///./sirius_sklad.db

# Настройки безопасности
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки приложения
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Настройки загрузки файлов
UPLOAD_DIR=app/static/uploads
MAX_FILE_SIZE=10485760
EOF
    echo "⚠️ ВНИМАНИЕ: Измените SECRET_KEY в .env файле!"
fi

# Создаем необходимые папки
echo "📁 Создаем папки..."
mkdir -p app/static/uploads
mkdir -p app/static/qr
mkdir -p logs

# Применяем миграции
echo "🗄️ Применяем миграции базы данных..."
alembic upgrade head

echo "✅ Развертывание завершено!"
echo ""
echo "🚀 Запуск сервера:"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Доступные страницы:"
echo "   - Админка: http://localhost:8000/"
echo "   - Магазин: http://localhost:8000/shop"
echo "   - API docs: http://localhost:8000/docs"
