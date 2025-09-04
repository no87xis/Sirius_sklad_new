@echo off & chcp 65001 >nul
REM Простая остановка сервера

echo Остановка сервера...
taskkill /f /im python.exe
echo Сервер остановлен
pause
