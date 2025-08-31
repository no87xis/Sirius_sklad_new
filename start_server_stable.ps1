# Стабильный скрипт запуска сервера Sirius
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Sirius Server (STABLE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Активируем виртуальное окружение
    Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate virtual environment"
    }
    Write-Host "Virtual environment activated" -ForegroundColor Green

    # Проверяем зависимости
    Write-Host "[2/4] Checking dependencies..." -ForegroundColor Yellow
    python -c "import fastapi, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
    }
    Write-Host "Dependencies OK" -ForegroundColor Green

    # Проверяем конфигурацию
    Write-Host "[3/4] Checking configuration..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env file..." -ForegroundColor Yellow
        Copy-Item "env.example" ".env" -ErrorAction SilentlyContinue
    }
    Write-Host "Configuration OK" -ForegroundColor Green

    # Запускаем сервер
    Write-Host "[4/4] Starting server..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Server will start on http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Запускаем сервер с правильными параметрами
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Server startup failed!" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to continue"
