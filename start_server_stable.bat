@echo off
echo ========================================
echo    Starting Sirius Server (STABLE)
echo ========================================
echo.

REM Активируем виртуальное окружение
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated

REM Проверяем зависимости
echo [2/4] Checking dependencies...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo ERROR: Dependencies not installed
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo Dependencies OK

REM Проверяем конфигурацию
echo [3/4] Checking configuration...
if not exist ".env" (
    echo Creating .env file...
    copy env.example .env >nul
)
echo Configuration OK

REM Запускаем сервер
echo [4/4] Starting server...
echo.
echo Server will start on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Запускаем сервер с правильными параметрами
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
