@echo off & chcp 65001 >nul
REM Скрипт для создания админа

echo ========================================
echo   Создание администратора
echo ========================================
echo.

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Создаем администратора...
python scripts\create_test_admin.py

echo.
echo Готово! Теперь можно войти как:
echo Логин: admin
echo Пароль: admin123
echo.
pause
