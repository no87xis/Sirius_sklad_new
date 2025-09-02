# PowerShell скрипт для запуска диагностики Sirius Group
# Решает проблемы с зависаниями и командами

Write-Host "🚀 Запуск диагностики Sirius Group..." -ForegroundColor Blue
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

# Запускаем диагностику
Write-Host "✅ Запускаю диагностику..." -ForegroundColor Green
python diagnose_and_fix.py

# Проверяем результат
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Диагностика завершена успешно!" -ForegroundColor Green
    Write-Host "Теперь можно запускать сервер" -ForegroundColor Blue
} else {
    Write-Host "❌ Диагностика завершилась с ошибками!" -ForegroundColor Red
}

Write-Host "==================================================" -ForegroundColor Blue
Write-Host "Нажмите любую клавишу для продолжения..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
