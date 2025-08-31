@echo off
setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-dev" goto install-dev
if "%1"=="test" goto test
if "%1"=="test-cov" goto test-cov
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="clean" goto clean
if "%1"=="run" goto run
if "%1"=="run-prod" goto run-prod
if "%1"=="docker-build" goto docker-build
if "%1"=="docker-run" goto docker-run
if "%1"=="migrate-upgrade" goto migrate-upgrade
if "%1"=="migrate-downgrade" goto migrate-downgrade
if "%1"=="security-check" goto security-check
if "%1"=="ci" goto ci
if "%1"=="setup" goto setup
goto unknown

:help
echo Доступные команды:
echo   help              Показать справку по командам
echo   install           Установить зависимости
echo   install-dev       Установить зависимости для разработки
echo   test              Запустить тесты
echo   test-cov          Запустить тесты с покрытием
echo   lint              Проверить код линтерами
echo   format            Форматировать код
echo   clean             Очистить временные файлы
echo   run               Запустить сервер разработки
echo   run-prod          Запустить production сервер
echo   docker-build      Собрать Docker образ
echo   docker-run        Запустить Docker контейнер
echo   migrate-upgrade   Применить миграции
echo   migrate-downgrade Откатить миграции
echo   security-check    Проверить безопасность
echo   ci                Запустить все проверки CI
echo   setup             Настройка проекта с нуля
goto end

:install
echo Устанавливаю зависимости...
pip install -r requirements.txt
goto end

:install-dev
echo Устанавливаю зависимости для разработки...
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx black isort flake8 mypy bandit safety
goto end

:test
echo Запускаю тесты...
python -m pytest tests/ -v
goto end

:test-cov
echo Запускаю тесты с покрытием...
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
goto end

:lint
echo Проверяю код...
echo Flake8:
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
echo Black:
black --check app/
echo Isort:
isort --check-only app/
echo Mypy:
mypy app/ --ignore-missing-imports
goto end

:format
echo Форматирую код...
black app/
isort app/
goto end

:clean
echo Очищаю временные файлы...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.mypy_cache) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /s /q *.pyd 2>nul
del /s /q .coverage 2>nul
if exist htmlcov rd /s /q htmlcov
if exist .coverage del .coverage
if exist dist rd /s /q dist
if exist build rd /s /q build
goto end

:run
echo Запускаю сервер разработки...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
goto end

:run-prod
echo Запускаю production сервер...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
goto end

:docker-build
echo Собираю Docker образ...
docker build -t sirius-sklad:latest .
goto end

:docker-run
echo Запускаю Docker контейнер...
docker run -p 8000:8000 --env-file .env sirius-sklad:latest
goto end

:migrate-upgrade
echo Применяю миграции...
alembic upgrade head
goto end

:migrate-downgrade
echo Откатываю миграции...
set /p revision="Введите ревизию для отката: "
alembic downgrade %revision%
goto end

:security-check
echo Проверяю безопасность...
bandit -r app/ -f json -o bandit-report.json
safety check --json --output safety-report.json
goto end

:ci
echo Запускаю все проверки CI...
call :lint
call :test-cov
call :security-check
goto end

:setup
echo Настраиваю проект...
call :install-dev
call :format
call :test
echo Проект настроен!
echo Для запуска используйте: scripts\dev.bat run
goto end

:unknown
echo Неизвестная команда: %1
call :help
goto end

:end
endlocal
