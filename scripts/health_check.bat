@echo off
echo 🔍 Проверка здоровья системы Сириус...
echo.

REM Активация виртуального окружения
call "d:\Sirius_sklad_new\venv\Scripts\Activate.bat"

echo 📋 Проверка 1: Импорт приложения...
python -c "import app.main; print('✅ Импорт успешен')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка импорта
    goto :error
)

echo 📋 Проверка 2: Синтаксис main.py...
python -m py_compile app/main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка синтаксиса в main.py
    goto :error
)

echo 📋 Проверка 3: Синтаксис config.py...
python -m py_compile app/config.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка синтаксиса в config.py
    goto :error
)

echo 📋 Проверка 4: Синтаксис products.py...
python -m py_compile app/services/products.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ошибка синтаксиса в products.py
    goto :error
)

echo 📋 Проверка 5: Статус порта 8000...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ⚠️  Порт 8000 занят
    echo Процессы на порту 8000:
    netstat -ano | findstr :8000
) else (
    echo ✅ Порт 8000 свободен
)

echo 📋 Проверка 6: Процессы Python...
tasklist | findstr python >nul
if %errorlevel% equ 0 (
    echo ⚠️  Найдены процессы Python:
    tasklist | findstr python
) else (
    echo ✅ Процессы Python не запущены
)

echo.
echo 🎯 Проверка завершена!
echo.
echo 📚 Рекомендации:
echo - Если есть ошибки синтаксиса - исправьте их
echo - Если порт занят - используйте start_server.bat
echo - Для запуска сервера используйте start_server.bat
echo.
goto :end

:error
echo.
echo ❌ Обнаружены критические ошибки!
echo Исправьте ошибки перед запуском сервера
echo.

:end
pause






