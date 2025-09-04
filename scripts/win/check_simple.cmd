@echo off & chcp 65001 >nul
REM Простая проверка сервера

echo Проверка сервера...
echo.
echo Процессы Python:
tasklist | findstr python
echo.
echo Порт 8000:
netstat -an | findstr :8000
echo.
echo Health endpoints:
curl -s http://127.0.0.1:8000/health 2>nul || echo Сервер не отвечает
curl -s http://127.0.0.1:8000/api/health 2>nul || echo API не отвечает
echo.
pause
