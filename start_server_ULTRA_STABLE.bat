@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 SIRIUS SERVER - ULTRA STABLE LAUNCH
echo ========================================
echo.

:: Останавливаем все процессы Python на порту 8000
echo 🔴 Останавливаем старые процессы...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1

:: Ждем завершения
timeout /t 2 /nobreak >nul

:: Проверяем порт
echo 🔍 Проверяем порт 8000...
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ❌ Порт 8000 все еще занят!
    echo 🔴 Принудительно освобождаем порт...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 1 /nobreak >nul
)

:: Активируем виртуальное окружение
echo 🟢 Активируем виртуальное окружение...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не удалось активировать venv!
    pause
    exit /b 1
)

:: Проверяем зависимости
echo 🔍 Проверяем зависимости...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Зависимости не установлены!
    echo 📦 Устанавливаем зависимости...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ ОШИБКА: Не удалось установить зависимости!
        pause
        exit /b 1
    )
)

:: Проверяем импорт приложения
echo 🔍 Проверяем приложение...
python -c "from app.main import app" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Приложение не импортируется!
    echo 🔍 Запускаем диагностику...
    python test_minimal_server.py
    pause
    exit /b 1
)

:: Запускаем сервер
echo 🚀 Запускаем сервер...
echo.
echo ========================================
echo ✅ СЕРВЕР ЗАПУСКАЕТСЯ...
echo 🌐 Адрес: http://127.0.0.1:8000
echo 🛑 Для остановки нажмите Ctrl+C
echo ========================================
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

:: Если сервер упал
echo.
echo ❌ Сервер остановлен!
echo 🔄 Перезапуск через 5 секунд...
timeout /t 5 /nobreak >nul
goto :start_server_ULTRA_STABLE.bat
