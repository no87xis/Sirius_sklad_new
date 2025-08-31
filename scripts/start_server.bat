@echo off
echo 🚀 Запуск сервера Сириус...
echo.

REM Активация виртуального окружения
echo 📦 Активация виртуального окружения...
call "d:\Sirius_sklad_new\venv\Scripts\Activate.bat"

REM Проверка порта
echo 🔍 Проверка порта 8000...
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo ⚠️  Порт 8000 занят. Завершение процессов...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo Завершение процесса PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM Проверка импорта
echo 🔍 Проверка импорта приложения...
python -c "import app.main; print('✅ Импорт успешен')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка импорта приложения
    echo Проверьте код на синтаксические ошибки
    pause
    exit /b 1
)

REM Запуск сервера
echo 🚀 Запуск сервера...
echo Сервер будет доступен по адресу: http://127.0.0.1:8000
echo Для остановки нажмите Ctrl+C
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo ✅ Сервер остановлен
pause

