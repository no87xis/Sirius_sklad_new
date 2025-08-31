.PHONY: help install install-dev test test-cov lint format clean run docker-build docker-run migrate migrate-upgrade migrate-downgrade

# Переменные
PYTHON = python
PIP = pip
PYTEST = pytest
UVICORN = uvicorn
APP = app.main:app
PORT = 8000
HOST = 127.0.0.1

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Устанавливаю зависимости...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Устанавливаю зависимости для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

test: ## Запустить тесты
	@echo "$(GREEN)Запускаю тесты...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запускаю тесты с покрытием...$(NC)"
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing

lint: ## Проверить код линтерами
	@echo "$(GREEN)Проверяю код...$(NC)"
	@echo "$(YELLOW)Flake8:$(NC)"
	flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "$(YELLOW)Black:$(NC)"
	black --check app/
	@echo "$(YELLOW)Isort:$(NC)"
	isort --check-only app/
	@echo "$(YELLOW)Mypy:$(NC)"
	mypy app/ --ignore-missing-imports

format: ## Форматировать код
	@echo "$(GREEN)Форматирую код...$(NC)"
	black app/
	isort app/

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очищаю временные файлы...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

run: ## Запустить сервер разработки
	@echo "$(GREEN)Запускаю сервер разработки...$(NC)"
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

run-prod: ## Запустить сервер production
	@echo "$(GREEN)Запускаю production сервер...$(NC)"
	$(UVICORN) $(APP) --host 0.0.0.0 --port $(PORT)

docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Собираю Docker образ...$(NC)"
	docker build -t sirius-sklad:latest .

docker-run: ## Запустить Docker контейнер
	@echo "$(GREEN)Запускаю Docker контейнер...$(NC)"
	docker run -p $(PORT):$(PORT) --env-file .env sirius-sklad:latest

migrate: ## Создать новую миграцию
	@echo "$(GREEN)Создаю новую миграцию...$(NC)"
	@read -p "Введите описание миграции: " description; \
	alembic revision --autogenerate -m "$$description"

migrate-upgrade: ## Применить миграции
	@echo "$(GREEN)Применяю миграции...$(NC)"
	alembic upgrade head

migrate-downgrade: ## Откатить миграции
	@echo "$(GREEN)Откатываю миграции...$(NC)"
	@read -p "Введите ревизию для отката: " revision; \
	alembic downgrade $$revision

security-check: ## Проверить безопасность
	@echo "$(GREEN)Проверяю безопасность...$(NC)"
	bandit -r app/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true

ci: ## Запустить все проверки CI
	@echo "$(GREEN)Запускаю все проверки CI...$(NC)"
	$(MAKE) lint
	$(MAKE) test-cov
	$(MAKE) security-check

setup: ## Настройка проекта с нуля
	@echo "$(GREEN)Настраиваю проект...$(NC)"
	$(MAKE) install-dev
	$(MAKE) format
	$(MAKE) test
	@echo "$(GREEN)Проект настроен!$(NC)"
	@echo "$(YELLOW)Для запуска используйте: make run$(NC)"
