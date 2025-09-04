@echo off & chcp 65001 >nul
REM Скрипт для исправления роли админа

echo ========================================
echo   Исправление роли админа
echo ========================================
echo.

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Исправляем роль админа...
python fix_admin_role.py

echo.
echo Готово! Теперь можно войти как:
echo Логин: admin
echo Пароль: admin123
echo.
pause
