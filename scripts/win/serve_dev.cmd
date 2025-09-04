@echo off & chcp 65001 >nul
REM Sirius Group - Запуск dev-сервера
REM Запускает uvicorn сервер в режиме разработки с автоматическим перезапуском

echo.
echo ========================================
echo   Sirius Group - Запуск dev-сервера
echo ========================================
echo.

REM Проверяем, что мы в правильной директории
if not exist "app\main.py" (
    echo ОШИБКА: app\main.py не найден. Запустите скрипт из корня проекта.
    pause
    exit /b 1
)

REM Проверяем виртуальное окружение
if not exist "venv\Scripts\activate.bat" (
    echo ОШИБКА: Виртуальное окружение не найдено в venv\
    echo Создайте виртуальное окружение: python -m venv venv
    pause
    exit /b 1
)

REM Создаем папку logs если её нет
if not exist "logs" mkdir logs

REM Проверяем, не запущен ли уже сервер
if exist "logs\uvicorn-dev.pid" (
    echo ПРЕДУПРЕЖДЕНИЕ: Файл PID найден. Возможно, сервер уже запущен.
    echo Проверьте статус: scripts\win\serve_status.cmd
    echo Или остановите сервер: scripts\win\serve_stop.cmd
    pause
    exit /b 1
)

REM Проверяем, не занят ли порт 8000
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ОШИБКА: Порт 8000 уже занят. Остановите другой сервер или измените порт.
    pause
    exit /b 1
)

echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo Проверяем зависимости...
python -c "import fastapi, uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo ОШИБКА: Зависимости не установлены. Установите: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Запускаем dev-сервер...
echo Логи будут записываться в: logs\uvicorn-dev.log
echo PID будет сохранен в: logs\uvicorn-dev.pid
echo.
echo Для остановки сервера используйте: scripts\win\serve_stop.cmd
echo Для проверки статуса используйте: scripts\win\serve_status.cmd
echo.
echo Сервер будет доступен по адресу: http://127.0.0.1:8000
echo.

REM Запускаем uvicorn в отдельном окне с редиректом вывода
start "" cmd /c "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info > logs\uvicorn-dev.log 2>&1"

REM Ждем запуска сервера
timeout /t 3 /nobreak >nul

REM Находим PID процесса uvicorn и сохраняем
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /v "INFO"') do (
    echo %%i > logs\uvicorn-dev.pid
    goto :pid_saved
)
echo 0 > logs\uvicorn-dev.pid
:pid_saved

REM Ждем немного и проверяем, что сервер запустился
timeout /t 3 /nobreak >nul

REM Проверяем, что PID файл создался
if exist "logs\uvicorn-dev.pid" (
    echo ✅ Сервер запущен успешно!
    echo.
    echo Откройте браузер и перейдите по адресу: http://127.0.0.1:8000
    echo.
    echo Для просмотра логов в реальном времени:
    echo   powershell Get-Content logs\uvicorn-dev.log -Wait -Tail 10
    echo.
) else (
    echo ❌ ОШИБКА: Не удалось запустить сервер
    echo Проверьте логи: logs\uvicorn-dev.log
    pause
    exit /b 1
)

echo Нажмите любую клавишу для выхода...
pause >nul
