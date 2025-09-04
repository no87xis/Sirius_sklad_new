@echo off & chcp 65001 >nul
REM Скрипт для перезапуска сервера

echo ========================================
echo   Перезапуск сервера
echo ========================================
echo.

echo Останавливаем старый сервер...
taskkill /f /im python.exe 2>nul

echo.
echo Ждем 2 секунды...
timeout /t 2 /nobreak >nul

echo.
echo Запускаем новый сервер...
start "" cmd /c "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo Сервер перезапущен!
echo Откройте: http://127.0.0.1:8000
echo.
pause
