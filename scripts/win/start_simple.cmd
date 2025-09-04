@echo off & chcp 65001 >nul
REM Простой запуск сервера без сложной логики

echo Запуск сервера...
start "" cmd /c "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo Сервер запущен в отдельном окне
echo Откройте: http://127.0.0.1:8000
pause
