# SIRIUS SERVER - ULTRA STABLE LAUNCH (PowerShell)
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 SIRIUS SERVER - ULTRA STABLE LAUNCH" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Останавливаем все процессы Python на порту 8000
Write-Host "🔴 Останавливаем старые процессы..." -ForegroundColor Red
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Ждем завершения
Start-Sleep -Seconds 2

# Проверяем порт
Write-Host "🔍 Проверяем порт 8000..." -ForegroundColor Yellow
$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "❌ Порт 8000 все еще занят!" -ForegroundColor Red
    Write-Host "🔴 Принудительно освобождаем порт..." -ForegroundColor Red
    foreach ($connection in $portCheck) {
        Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

# Активируем виртуальное окружение
Write-Host "🟢 Активируем виртуальное окружение..." -ForegroundColor Green
try {
    & ".\venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate venv"
    }
} catch {
    Write-Host "❌ ОШИБКА: Не удалось активировать venv!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Проверяем зависимости
Write-Host "🔍 Проверяем зависимости..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies not found"
    }
} catch {
    Write-Host "❌ ОШИБКА: Зависимости не установлены!" -ForegroundColor Red
    Write-Host "📦 Устанавливаем зависимости..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ОШИБКА: Не удалось установить зависимости!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
}

# Проверяем импорт приложения
Write-Host "🔍 Проверяем приложение..." -ForegroundColor Yellow
try {
    python -c "from app.main import app" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "App import failed"
    }
} catch {
    Write-Host "❌ ОШИБКА: Приложение не импортируется!" -ForegroundColor Red
    Write-Host "🔍 Запускаем диагностику..." -ForegroundColor Yellow
    python test_minimal_server.py
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Запускаем сервер
Write-Host "🚀 Запускаем сервер..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ СЕРВЕР ЗАПУСКАЕТСЯ..." -ForegroundColor Green
Write-Host "🌐 Адрес: http://127.0.0.1:8000" -ForegroundColor Blue
Write-Host "🛑 Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} catch {
    Write-Host ""
    Write-Host "❌ Сервер остановлен!" -ForegroundColor Red
    Write-Host "🔄 Перезапуск через 5 секунд..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    & $PSCommandPath
}
