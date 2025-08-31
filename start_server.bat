@echo off
echo ========================================
echo    Запуск сервера Сириус
echo ========================================
echo.

REM Активация виртуального окружения
echo [1/5] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения
    echo Убедитесь, что папка venv существует
    pause
    exit /b 1
)
echo ✓ Виртуальное окружение активировано

REM Проверка зависимостей
echo [2/5] Проверка зависимостей...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ❌ FastAPI не установлен
    echo Устанавливаем зависимости...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей
        pause
        exit /b 1
    )
)
echo ✓ Зависимости проверены

REM Создание .env файла
echo [3/5] Проверка конфигурации...
if not exist .env (
    echo Создаем .env файл...
    copy env.example .env >nul
    echo ✓ .env файл создан
) else (
    echo ✓ .env файл существует
)

REM Проверка миграций
echo [4/5] Проверка миграций базы данных...
alembic current >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка проверки миграций
    echo Возможно, база данных повреждена
) else (
    echo ✓ Миграции в порядке
)

REM Запуск сервера
echo [5/5] Запуск сервера...
echo.
echo Сервер запускается на http://127.0.0.1:8000
echo Для остановки нажмите Ctrl+C
echo.
python test_server_debug.py

pause
