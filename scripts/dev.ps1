# Скрипт для команд разработки Сириус
param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Цвета для вывода
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

# Функции
function Write-Info {
    param([string]$Message)
    Write-Host "$Green$Message$Reset"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$Yellow$Message$Reset"
}

function Write-Error {
    param([string]$Message)
    Write-Host "$Red$Message$Reset"
}

function Show-Help {
    Write-Info "Доступные команды:"
    Write-Host "  $Yellow{'help'}$Reset          Показать справку по командам"
    Write-Host "  $Yellow{'install'}$Reset       Установить зависимости"
    Write-Host "  $Yellow{'install-dev'}$Reset   Установить зависимости для разработки"
    Write-Host "  $Yellow{'test'}$Reset          Запустить тесты"
    Write-Host "  $Yellow{'test-cov'}$Reset      Запустить тесты с покрытием"
    Write-Host "  $Yellow{'lint'}$Reset          Проверить код линтерами"
    Write-Host "  $Yellow{'format'}$Reset        Форматировать код"
    Write-Host "  $Yellow{'clean'}$Reset         Очистить временные файлы"
    Write-Host "  $Yellow{'run'}$Reset           Запустить сервер разработки"
    Write-Host "  $Yellow{'run-prod'}$Reset      Запустить production сервер"
    Write-Host "  $Yellow{'docker-build'}$Reset  Собрать Docker образ"
    Write-Host "  $Yellow{'docker-run'}$Reset    Запустить Docker контейнер"
    Write-Host "  $Yellow{'migrate-upgrade'}$Reset Применить миграции"
    Write-Host "  $Yellow{'migrate-downgrade'}$Reset Откатить миграции"
    Write-Host "  $Yellow{'security-check'}$Reset Проверить безопасность"
    Write-Host "  $Yellow{'ci'}$Reset            Запустить все проверки CI"
    Write-Host "  $Yellow{'setup'}$Reset         Настройка проекта с нуля"
}

function Install-Dependencies {
    Write-Info "Устанавливаю зависимости..."
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Info "Устанавливаю зависимости для разработки..."
    pip install -r requirements.txt
    pip install pytest pytest-cov pytest-asyncio httpx black isort flake8 mypy bandit safety
}

function Run-Tests {
    Write-Info "Запускаю тесты..."
    python -m pytest tests/ -v
}

function Run-TestsWithCoverage {
    Write-Info "Запускаю тесты с покрытием..."
    python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
}

function Check-Lint {
    Write-Info "Проверяю код..."
    Write-Warning "Flake8:"
    flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
    Write-Warning "Black:"
    black --check app/
    Write-Warning "Isort:"
    isort --check-only app/
    Write-Warning "Mypy:"
    mypy app/ --ignore-missing-imports
}

function Format-Code {
    Write-Info "Форматирую код..."
    black app/
    isort app/
}

function Clean-Project {
    Write-Info "Очищаю временные файлы..."
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object { Remove-Item -Recurse -Force $_ }
    Get-ChildItem -Recurse -File -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -File -Name "*.pyo" | Remove-Item -Force
    Get-ChildItem -Recurse -File -Name "*.pyd" | Remove-Item -Force
    Get-ChildItem -Recurse -File -Name ".coverage" | Remove-Item -Force
    Get-ChildItem -Recurse -Directory -Name "*.egg-info" | ForEach-Object { Remove-Item -Recurse -Force $_ }
    Get-ChildItem -Recurse -Directory -Name ".pytest_cache" | ForEach-Object { Remove-Item -Recurse -Force $_ }
    Get-ChildItem -Recurse -Directory -Name ".mypy_cache" | ForEach-Object { Remove-Item -Recurse -Force $_ }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
}

function Start-DevServer {
    Write-Info "Запускаю сервер разработки..."
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}

function Start-ProdServer {
    Write-Info "Запускаю production сервер..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
}

function Build-Docker {
    Write-Info "Собираю Docker образ..."
    docker build -t sirius-sklad:latest .
}

function Run-Docker {
    Write-Info "Запускаю Docker контейнер..."
    docker run -p 8000:8000 --env-file .env sirius-sklad:latest
}

function Update-Migrations {
    Write-Info "Применяю миграции..."
    alembic upgrade head
}

function Downgrade-Migrations {
    Write-Info "Откатываю миграции..."
    $revision = Read-Host "Введите ревизию для отката"
    alembic downgrade $revision
}

function Check-Security {
    Write-Info "Проверяю безопасность..."
    bandit -r app/ -f json -o bandit-report.json
    safety check --json --output safety-report.json
}

function Run-CI {
    Write-Info "Запускаю все проверки CI..."
    Check-Lint
    Run-TestsWithCoverage
    Check-Security
}

function Setup-Project {
    Write-Info "Настраиваю проект..."
    Install-DevDependencies
    Format-Code
    Run-Tests
    Write-Info "Проект настроен!"
    Write-Warning "Для запуска используйте: .\scripts\dev.ps1 run"
}

# Основная логика
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "lint" { Check-Lint }
    "format" { Format-Code }
    "clean" { Clean-Project }
    "run" { Start-DevServer }
    "run-prod" { Start-ProdServer }
    "docker-build" { Build-Docker }
    "docker-run" { Run-Docker }
    "migrate-upgrade" { Update-Migrations }
    "migrate-downgrade" { Downgrade-Migrations }
    "security-check" { Check-Security }
    "ci" { Run-CI }
    "setup" { Setup-Project }
    default {
        Write-Error "Неизвестная команда: $Command"
        Show-Help
    }
}
