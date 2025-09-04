@echo off & chcp 65001 >nul
REM Sirius Group - Проверка статуса dev-сервера
REM Показывает статус сервера, порты и последние логи

echo.
echo ========================================
echo   Sirius Group - Статус dev-сервера
echo ========================================
echo.

REM Проверяем, что мы в правильной директории
if not exist "app\main.py" (
    echo ОШИБКА: app\main.py не найден. Запустите скрипт из корня проекта.
    pause
    exit /b 1
)

echo 📊 СТАТУС СЕРВЕРА:
echo.

REM Проверяем наличие PID файла
if exist "logs\uvicorn-dev.pid" (
    set /p SERVER_PID=<logs\uvicorn-dev.pid
    echo ✅ PID файл найден: %SERVER_PID%
    
    REM Проверяем, существует ли процесс
    tasklist /fi "PID eq %SERVER_PID%" | findstr %SERVER_PID% >nul
    if %errorlevel% equ 0 (
        echo ✅ Процесс активен (PID: %SERVER_PID%)
    ) else (
        echo ❌ Процесс не найден (PID: %SERVER_PID%)
        echo    Возможно, сервер упал. Удалите PID файл.
    )
) else (
    echo ❌ PID файл не найден
    echo    Сервер не запущен через serve_dev.cmd
)

echo.

echo 🌐 СТАТУС ПОРТА 8000:
echo.
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ✅ Порт 8000 занят:
    netstat -ano | findstr :8000
    echo.
    echo 🔗 Сервер доступен по адресу: http://127.0.0.1:8000
) else (
    echo ❌ Порт 8000 свободен
    echo    Сервер не запущен
)

echo.

echo 🐍 ПРОЦЕССЫ PYTHON:
echo.
tasklist | findstr python >nul
if %errorlevel% equ 0 (
    echo ✅ Найдены процессы Python:
    tasklist | findstr python
) else (
    echo ❌ Процессы Python не найдены
)

echo.

echo 📝 ПОСЛЕДНИЕ ЛОГИ (последние 10 строк):
echo.
if exist "logs\uvicorn-dev.log" (
    echo Файл логов: logs\uvicorn-dev.log
    echo.
    powershell -Command "Get-Content 'logs\uvicorn-dev.log' -Tail 10 -ErrorAction SilentlyContinue"
    if %errorlevel% neq 0 (
        echo ❌ Ошибка чтения логов
    )
) else (
    echo ❌ Файл логов не найден: logs\uvicorn-dev.log
)

echo.

echo 📁 ФАЙЛЫ ЛОГОВ:
echo.
if exist "logs" (
    echo Папка logs существует:
    dir logs /b 2>nul
    if %errorlevel% neq 0 (
        echo    (папка пуста)
    )
) else (
    echo ❌ Папка logs не существует
)

echo.

echo 🛠️  КОМАНДЫ УПРАВЛЕНИЯ:
echo.
echo   Запуск сервера:    scripts\win\serve_dev.cmd
echo   Остановка сервера: scripts\win\serve_stop.cmd
echo   Проверка статуса:  scripts\win\serve_status.cmd
echo   Сборка проекта:    scripts\win\make.bat
echo.

echo 📖 ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ:
echo.
echo   Просмотр логов в реальном времени:
echo     powershell Get-Content logs\uvicorn-dev.log -Wait -Tail 10
echo.
echo   Проверка доступности сервера:
echo     curl http://127.0.0.1:8000/
echo.

echo Нажмите любую клавишу для выхода...
pause >nul
