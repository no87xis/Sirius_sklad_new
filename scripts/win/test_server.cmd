@echo off & chcp 65001 >nul
REM Простой тест сервера

echo.
echo ========================================
echo   Тест сервера
echo ========================================
echo.

REM Проверяем процессы Python
echo 🐍 ПРОЦЕССЫ PYTHON:
tasklist | findstr python
echo.

REM Проверяем порт 8000
echo 🌐 ПОРТ 8000:
netstat -an | findstr :8000
echo.

REM Проверяем PID файл
echo 📁 PID ФАЙЛ:
if exist "logs\uvicorn-dev.pid" (
    type logs\uvicorn-dev.pid
) else (
    echo Файл не найден
)
echo.

REM Проверяем логи
echo 📝 ПОСЛЕДНИЕ ЛОГИ:
if exist "logs\uvicorn-dev.log" (
    powershell -Command "Get-Content 'logs\uvicorn-dev.log' -Tail 5 -ErrorAction SilentlyContinue"
) else (
    echo Файл логов не найден
)
echo.

pause
