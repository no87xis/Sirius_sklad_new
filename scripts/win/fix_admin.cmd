@echo off & chcp 65001 >nul
REM Скрипт для исправления админа

echo ========================================
echo   Исправление администратора
echo ========================================
echo.

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Исправляем админа...
python fix_admin_simple.py

echo.
echo Готово! Теперь можно войти как:
echo Логин: admin
echo Пароль: admin123
echo.
pause
