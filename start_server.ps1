# PowerShell скрипт для запуска сервера Sirius Group
# Решает проблемы с зависаниями и командами

Write-Host "🚀 Запуск сервера Sirius Group..." -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Активируем виртуальное окружение
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Активирую виртуальное окружение..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    exit 1
}

# Проверяем Python
Write-Host "✅ Проверяю Python..." -ForegroundColor Green
python --version

# Проверяем зависимости
Write-Host "✅ Проверяю зависимости..." -ForegroundColor Green
if (Test-Path "requirements.txt") {
    Write-Host "Устанавливаю/обновляю зависимости..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt не найден, пропускаю установку зависимостей" -ForegroundColor Yellow
}

# Запускаем сервер
Write-Host "✅ Запускаю сервер..." -ForegroundColor Green
Write-Host "Сервер будет доступен по адресу: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Blue

# Запускаем uvicorn
try {
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "❌ Ошибка запуска сервера: $_" -ForegroundColor Red
    Write-Host "Попробуйте запустить диагностику: .\run_diagnosis.ps1" -ForegroundColor Yellow
}

Write-Host "==================================================" -ForegroundColor Blue
Write-Host "Нажмите любую клавишу для продолжения..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
