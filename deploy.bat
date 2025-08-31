@echo off
chcp 65001 >nul
echo 🚀 Начинаем развертывание Sirius Group...

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)

REM Создаем виртуальное окружение
echo 📦 Создаем виртуальное окружение...
python -m venv venv
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo 📥 Устанавливаем зависимости...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Создаем .env файл если его нет
if not exist .env (
    echo ⚙️ Создаем .env файл...
    (
        echo DATABASE_URL=sqlite:///./sirius_sklad.db
        echo SECRET_KEY=your-secret-key-change-this-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo DEBUG=False
        echo HOST=0.0.0.0
        echo PORT=8000
        echo UPLOAD_DIR=app/static/uploads
        echo MAX_FILE_SIZE=10485760
    ) > .env
    echo ⚠️ ВНИМАНИЕ: Измените SECRET_KEY в .env файле!
)

REM Создаем папки для загрузок
echo 📁 Создаем папки...
if not exist app\static\uploads mkdir app\static\uploads
if not exist logs mkdir logs

REM Применяем миграции
echo 🗄️ Применяем миграции базы данных...
alembic upgrade head

REM Создаем .gitkeep для uploads
echo. > app\static\uploads\.gitkeep

echo ✅ Развертывание завершено!
echo 🚀 Запуск сервера:
echo    venv\Scripts\activate.bat
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 🌐 Доступные страницы:
echo    - Админка: http://localhost:8000/
echo    - Магазин: http://localhost:8000/shop
echo    - API docs: http://localhost:8000/docs
pause
