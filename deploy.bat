@echo off
echo 🚀 Начинаем развертывание Sirius Group...

REM Создаем виртуальное окружение
echo 📦 Создаем виртуальное окружение...
python -m venv venv
call venv\Scripts\activate.bat

REM Обновляем pip
pip install --upgrade pip

REM Устанавливаем зависимости
echo 📥 Устанавливаем зависимости...
pip install -r requirements.txt

REM Дополнительные зависимости
echo 📦 Устанавливаем дополнительные зависимости...
pip install pydantic-settings itsdangerous qrcode pillow

REM Создаем .env файл если его нет
echo ⚙️ Создаем .env файл...
if not exist .env (
    (
        echo # Настройки базы данных
        echo DATABASE_URL=sqlite:///./sirius_sklad.db
        echo.
        echo # Настройки безопасности
        echo SECRET_KEY=your-secret-key-change-this-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # Настройки приложения
        echo DEBUG=True
        echo HOST=0.0.0.0
        echo PORT=8000
        echo.
        echo # Настройки загрузки файлов
        echo UPLOAD_DIR=app/static/uploads
        echo MAX_FILE_SIZE=10485760
    ) > .env
    echo ⚠️ ВНИМАНИЕ: Измените SECRET_KEY в .env файле!
)

REM Создаем необходимые папки
echo 📁 Создаем папки...
if not exist app\static\uploads mkdir app\static\uploads
if not exist app\static\qr mkdir app\static\qr
if not exist logs mkdir logs

REM Применяем миграции
echo 🗄️ Применяем миграции базы данных...
alembic upgrade head

echo ✅ Развертывание завершено!
echo.
echo 🚀 Запуск сервера:
echo    venv\Scripts\activate.bat
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 🌐 Доступные страницы:
echo    - Админка: http://localhost:8000/
echo    - Магазин: http://localhost:8000/shop
echo    - API docs: http://localhost:8000/docs

pause
