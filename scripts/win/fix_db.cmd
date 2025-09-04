@echo off & chcp 65001 >nul
REM Скрипт для исправления базы данных

echo ========================================
echo   Исправление базы данных
echo ========================================
echo.

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Исправляем схему базы данных...
python fix_db_schema.py

echo.
echo Готово! Теперь можно войти как:
echo Логин: admin
echo Пароль: admin123
echo.
pause
