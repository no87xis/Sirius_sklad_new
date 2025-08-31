# Start Sirius Server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Sirius Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/5] Activating virtual environment..." -ForegroundColor Yellow
try {
    & "venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Make sure venv folder exists" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "[2/5] Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import fastapi" | Out-Null
    Write-Host "Dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "FastAPI not installed" -ForegroundColor Red
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create .env file
Write-Host "[3/5] Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host ".env file created" -ForegroundColor Green
} else {
    Write-Host ".env file exists" -ForegroundColor Green
}

# Check migrations
Write-Host "[4/5] Checking database migrations..." -ForegroundColor Yellow
try {
    alembic current | Out-Null
    Write-Host "Migrations OK" -ForegroundColor Green
} catch {
    Write-Host "Migration check failed" -ForegroundColor Red
    Write-Host "Database might be corrupted" -ForegroundColor Red
}

# Start server
Write-Host "[5/5] Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server starting on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python test_server_debug.py

Read-Host "Press Enter to exit"
