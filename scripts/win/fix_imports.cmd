@echo off & chcp 65001 >nul
REM Скрипт для исправления импортов

echo ========================================
echo   Исправление импортов
echo ========================================
echo.

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Проверяем импорты...
python -c "from app.constants import ProductStatus; print('✅ ProductStatus импортирован успешно')"

echo.
echo Готово!
pause
