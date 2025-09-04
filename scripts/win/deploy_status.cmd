@echo off & chcp 65001 >nul
REM Скрипт для проверки статуса деплоя

echo ========================================
echo   Статус деплоя
echo ========================================
echo.

echo 📊 СТАТУС GIT:
git status --short
echo.

echo 📝 ПОСЛЕДНИЕ КОММИТЫ:
git log --oneline -5
echo.

echo 🌐 СТАТУС СЕРВЕРА:
tasklist | findstr python
echo.

echo 🔗 ПОРТ 8000:
netstat -an | findstr :8000
echo.

echo 💚 HEALTH ENDPOINTS:
curl -s http://127.0.0.1:8000/health 2>nul || echo Сервер не отвечает
curl -s http://127.0.0.1:8000/api/health 2>nul || echo API не отвечает
echo.

pause
