@echo off & chcp 65001 >nul
REM Sirius Group - Остановка dev-сервера
REM Останавливает uvicorn сервер по PID

echo.
echo ========================================
echo   Sirius Group - Остановка dev-сервера
echo ========================================
echo.

REM Проверяем, что мы в правильной директории
if not exist "app\main.py" (
    echo ОШИБКА: app\main.py не найден. Запустите скрипт из корня проекта.
    pause
    exit /b 1
)

REM Проверяем наличие PID файла
if not exist "logs\uvicorn-dev.pid" (
    echo ИНФОРМАЦИЯ: Файл PID не найден. Сервер, вероятно, не запущен.
    echo.
    echo Проверяем процессы Python...
    tasklist | findstr python
    if %errorlevel% equ 0 (
        echo.
        echo Найдены процессы Python. Возможно, сервер запущен без PID файла.
        echo Для принудительной остановки всех Python процессов используйте:
        echo   taskkill /f /im python.exe
        echo.
    ) else (
        echo Процессы Python не найдены.
    )
    pause
    exit /b 0
)

echo Останавливаем dev-сервер...

REM Читаем PID из файла
set /p SERVER_PID=<logs\uvicorn-dev.pid

REM Проверяем, что PID - это число
echo %SERVER_PID% | findstr /r "^[0-9][0-9]*$" >nul
if %errorlevel% neq 0 (
    echo ОШИБКА: Неверный формат PID в файле logs\uvicorn-dev.pid
    echo Содержимое файла: %SERVER_PID%
    del logs\uvicorn-dev.pid
    pause
    exit /b 1
)

echo Найден PID: %SERVER_PID%

REM Проверяем, существует ли процесс с таким PID
tasklist /fi "PID eq %SERVER_PID%" | findstr %SERVER_PID% >nul
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Процесс с PID %SERVER_PID% не найден.
    echo Возможно, сервер уже остановлен.
    del logs\uvicorn-dev.pid
    echo ✅ PID файл удален.
    pause
    exit /b 0
)

REM Останавливаем процесс
echo Останавливаем процесс %SERVER_PID%...
taskkill /pid %SERVER_PID% /f >nul 2>&1

REM Ждем немного
timeout /t 2 /nobreak >nul

REM Проверяем, что процесс остановлен
tasklist /fi "PID eq %SERVER_PID%" | findstr %SERVER_PID% >nul
if %errorlevel% equ 0 (
    echo ❌ ОШИБКА: Не удалось остановить процесс %SERVER_PID%
    echo Попробуйте принудительную остановку:
    echo   taskkill /f /pid %SERVER_PID%
    pause
    exit /b 1
) else (
    echo ✅ Процесс %SERVER_PID% успешно остановлен.
)

REM Удаляем PID файл
del logs\uvicorn-dev.pid
echo ✅ PID файл удален.

REM Проверяем, что порт 8000 свободен
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: Порт 8000 все еще занят.
    echo Возможно, запущен другой сервер.
    echo.
    echo Процессы, использующие порт 8000:
    netstat -ano | findstr :8000
    echo.
) else (
    echo ✅ Порт 8000 свободен.
)

echo.
echo Сервер остановлен успешно!
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
