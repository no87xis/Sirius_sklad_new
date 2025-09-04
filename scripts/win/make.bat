@echo off & chcp 65001 >nul
REM Sirius Group - Сборка и подготовка проекта
REM Активирует окружение, устанавливает зависимости, применяет миграции

REM Проверяем аргументы командной строки
if "%1"=="up" goto :start_server
if "%1"=="down" goto :stop_server
if "%1"=="status" goto :check_status
if "%1"=="logs" goto :show_logs

REM Если аргументов нет, выполняем обычную сборку
goto :build_project

:start_server
echo.
echo ========================================
echo   Sirius Group - Запуск сервера
echo ========================================
echo.
call scripts\win\serve_dev.cmd
goto :end

:stop_server
echo.
echo ========================================
echo   Sirius Group - Остановка сервера
echo ========================================
echo.
call scripts\win\serve_stop.cmd
goto :end

:check_status
echo.
echo ========================================
echo   Sirius Group - Статус сервера
echo ========================================
echo.
call scripts\win\serve_status.cmd
goto :end

:show_logs
echo.
echo ========================================
echo   Sirius Group - Логи сервера
echo ========================================
echo.
if exist "logs\uvicorn-dev.log" (
    echo Последние 20 строк логов:
    echo.
    powershell -Command "Get-Content 'logs\uvicorn-dev.log' -Tail 20 -ErrorAction SilentlyContinue"
) else (
    echo Файл логов не найден: logs\uvicorn-dev.log
)
echo.
echo Для просмотра логов в реальном времени используйте:
echo   powershell Get-Content logs\uvicorn-dev.log -Wait -Tail 10
goto :end

:build_project
echo.
echo ========================================
echo   Sirius Group - Сборка проекта
echo ========================================
echo.

REM Проверяем, что мы в правильной директории
if not exist "app\main.py" (
    echo ОШИБКА: app\main.py не найден. Запустите скрипт из корня проекта.
    pause
    exit /b 1
)

echo 🔧 ПОДГОТОВКА ПРОЕКТА...
echo.

REM Проверяем Python
echo 1. Проверяем Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python найден
echo.

REM Проверяем/создаем виртуальное окружение
echo 2. Проверяем виртуальное окружение...
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Создаем виртуальное окружение...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ ОШИБКА: Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение найдено
)
echo.

REM Активируем виртуальное окружение
echo 3. Активируем виртуальное окружение...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано
echo.

REM Обновляем pip
echo 4. Обновляем pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  ПРЕДУПРЕЖДЕНИЕ: Не удалось обновить pip
)
echo.

REM Устанавливаем зависимости
echo 5. Устанавливаем зависимости...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ ОШИБКА: Не удалось установить зависимости
        pause
        exit /b 1
    )
    echo ✅ Зависимости установлены
) else (
    echo ❌ ОШИБКА: requirements.txt не найден
    pause
    exit /b 1
)
echo.

REM Проверяем основные модули
echo 6. Проверяем основные модули...
python -c "import fastapi, uvicorn, sqlalchemy, alembic" 2>nul
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не все зависимости установлены корректно
    echo Проверьте установку: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Основные модули доступны
echo.

REM Создаем папку logs
echo 7. Создаем папку logs...
if not exist "logs" mkdir logs
echo ✅ Папка logs готова
echo.

REM Проверяем базу данных
echo 8. Проверяем базу данных...
if exist "sirius.db" (
    echo ✅ База данных найдена: sirius.db
) else (
    echo ⚠️  База данных не найдена. Будет создана при первом запуске.
)
echo.

REM Применяем миграции (если есть)
echo 9. Проверяем миграции...
if exist "alembic.ini" (
    echo 📋 Применяем миграции Alembic...
    alembic current
    if %errorlevel% equ 0 (
        alembic upgrade head
        if %errorlevel% neq 0 (
            echo ⚠️  ПРЕДУПРЕЖДЕНИЕ: Не удалось применить миграции
        ) else (
            echo ✅ Миграции применены
        )
    ) else (
        echo ⚠️  ПРЕДУПРЕЖДЕНИЕ: Alembic не настроен
    )
) else (
    echo ℹ️  Миграции Alembic не настроены
)
echo.

REM Проверяем конфигурацию
echo 10. Проверяем конфигурацию...
if exist ".env" (
    echo ✅ Файл .env найден
) else (
    if exist "env.example" (
        echo 📋 Создаем .env из env.example...
        copy env.example .env
        echo ✅ Файл .env создан. Отредактируйте его при необходимости.
    ) else (
        echo ⚠️  ПРЕДУПРЕЖДЕНИЕ: Файлы конфигурации не найдены
    )
)
echo.

REM Финальная проверка
echo 11. Финальная проверка...
python -c "from app.main import app; print('✅ Приложение импортируется успешно')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Не удалось импортировать приложение
    echo Проверьте код в app/main.py
    pause
    exit /b 1
)
echo.

echo 🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!
echo.
echo 📋 СЛЕДУЮЩИЕ ШАГИ:
echo.
echo   1. Запустите dev-сервер:
echo      scripts\win\serve_dev.cmd
echo.
echo   2. Откройте браузер:
echo      http://127.0.0.1:8000
echo.
echo   3. Проверьте статус:
echo      scripts\win\serve_status.cmd
echo.
echo   4. Остановите сервер:
echo      scripts\win\serve_stop.cmd
echo.

echo Нажмите любую клавишу для выхода...
pause >nul
