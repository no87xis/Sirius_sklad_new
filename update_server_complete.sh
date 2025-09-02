#!/bin/bash

# =============================================================================
# КОМПЛЕКСНОЕ ОБНОВЛЕНИЕ СЕРВЕРА SIRIUS GROUP
# =============================================================================
# Этот скрипт полностью обновляет сервер с нуля
# Включает: остановку сервисов, обновление кода, миграции БД, перезапуск
# =============================================================================

set -e  # Остановка при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Использование: $0 <путь_к_проекту> [branch_name]"
    log_error "Пример: $0 /home/user/sirius main"
    exit 1
fi

PROJECT_PATH="$1"
BRANCH="${2:-main}"

# Проверка существования директории
if [ ! -d "$PROJECT_PATH" ]; then
    log_error "Директория $PROJECT_PATH не существует!"
    exit 1
fi

log_info "Начинаем комплексное обновление сервера Sirius Group"
log_info "Путь к проекту: $PROJECT_PATH"
log_info "Ветка: $BRANCH"

# Переходим в директорию проекта
cd "$PROJECT_PATH"

# =============================================================================
# ЭТАП 1: ОСТАНОВКА ВСЕХ СЕРВИСОВ
# =============================================================================
log_info "ЭТАП 1: Останавливаем все сервисы..."

# Останавливаем systemd сервисы
if systemctl is-active --quiet sirius.service 2>/dev/null; then
    log_info "Останавливаем sirius.service..."
    sudo systemctl stop sirius.service
    sudo systemctl disable sirius.service
fi

if systemctl is-active --quiet sirius-app.service 2>/dev/null; then
    log_info "Останавливаем sirius-app.service..."
    sudo systemctl stop sirius-app.service
    sudo systemctl disable sirius-app.service
fi

# Убиваем все процессы Python на порту 8000
log_info "Проверяем процессы на порту 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    log_info "Найдены процессы на порту 8000, останавливаем..."
    lsof -ti:8000 | xargs -r kill -9
fi

# Убиваем все процессы nohup
log_info "Останавливаем фоновые процессы..."
pkill -f "python.*main.py" || true
pkill -f "uvicorn.*main:app" || true

# Ждем завершения процессов
sleep 3

# Проверяем, что порт свободен
if lsof -ti:8000 > /dev/null 2>&1; then
    log_warning "Порт 8000 все еще занят, принудительно освобождаем..."
    lsof -ti:8000 | xargs -r kill -9
    sleep 2
fi

log_success "Все сервисы остановлены"

# =============================================================================
# ЭТАП 2: РЕЗЕРВНАЯ КОПИЯ БАЗЫ ДАННЫХ
# =============================================================================
log_info "ЭТАП 2: Создаем резервную копию базы данных..."

DB_PATH="app/database/sirius.db"
BACKUP_DIR="backups"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).db"

if [ -f "$DB_PATH" ]; then
    mkdir -p "$BACKUP_DIR"
    cp "$DB_PATH" "$BACKUP_DIR/$BACKUP_FILE"
    log_success "Резервная копия создана: $BACKUP_DIR/$BACKUP_FILE"
else
    log_warning "База данных не найдена, пропускаем резервное копирование"
fi

# =============================================================================
# ЭТАП 3: ОБНОВЛЕНИЕ КОДА ИЗ GIT
# =============================================================================
log_info "ЭТАП 3: Обновляем код из Git..."

# Сохраняем текущие изменения
log_info "Сохраняем текущие изменения..."
git stash push -m "Auto-stash before update $(date)" || true

# Переключаемся на нужную ветку
log_info "Переключаемся на ветку $BRANCH..."
git checkout "$BRANCH"

# Получаем последние изменения
log_info "Получаем последние изменения..."
git fetch origin

# Принудительно обновляем до последней версии
log_info "Принудительно обновляем до последней версии..."
git reset --hard "origin/$BRANCH"

# Очищаем неотслеживаемые файлы
log_info "Очищаем неотслеживаемые файлы..."
git clean -fd

log_success "Код обновлен до последней версии"

# =============================================================================
# ЭТАП 4: ОБНОВЛЕНИЕ ЗАВИСИМОСТЕЙ
# =============================================================================
log_info "ЭТАП 4: Обновляем зависимости..."

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    log_info "Активируем виртуальное окружение..."
    source venv/bin/activate
else
    log_info "Создаем новое виртуальное окружение..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Обновляем pip
log_info "Обновляем pip..."
pip install --upgrade pip

# Устанавливаем/обновляем зависимости
log_info "Устанавливаем зависимости..."
pip install -r requirements.txt

log_success "Зависимости обновлены"

# =============================================================================
# ЭТАП 5: ОБНОВЛЕНИЕ БАЗЫ ДАННЫХ
# =============================================================================
log_info "ЭТАП 5: Обновляем базу данных..."

# Создаем таблицы если их нет
log_info "Создаем таблицы базы данных..."
python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('База данных инициализирована')
"

# Запускаем миграции если есть
if [ -f "alembic.ini" ]; then
    log_info "Запускаем миграции Alembic..."
    alembic upgrade head || log_warning "Ошибка при миграциях, продолжаем..."
fi

log_success "База данных обновлена"

# =============================================================================
# ЭТАП 6: ПРОВЕРКА КОНФИГУРАЦИИ
# =============================================================================
log_info "ЭТАП 6: Проверяем конфигурацию..."

# Проверяем наличие необходимых файлов
REQUIRED_FILES=(
    "app/main.py"
    "app/database.py"
    "requirements.txt"
    ".env"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file найден"
    else
        log_warning "⚠ $file не найден"
    fi
done

# =============================================================================
# ЭТАП 7: ЗАПУСК СЕРВЕРА
# =============================================================================
log_info "ЭТАП 7: Запускаем сервер..."

# Создаем systemd сервис
log_info "Создаем systemd сервис..."

sudo tee /etc/systemd/system/sirius.service > /dev/null <<EOF
[Unit]
Description=Sirius Group Warehouse System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_PATH
Environment=PATH=$PROJECT_PATH/venv/bin
ExecStart=$PROJECT_PATH/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd и включаем сервис
sudo systemctl daemon-reload
sudo systemctl enable sirius.service
sudo systemctl start sirius.service

# Ждем запуска
log_info "Ждем запуска сервера..."
sleep 5

# Проверяем статус
if systemctl is-active --quiet sirius.service; then
    log_success "Сервис sirius.service успешно запущен"
else
    log_error "Ошибка запуска sirius.service"
    sudo systemctl status sirius.service
    exit 1
fi

# =============================================================================
# ЭТАП 8: ПРОВЕРКА РАБОТОСПОСОБНОСТИ
# =============================================================================
log_info "ЭТАП 8: Проверяем работоспособность..."

# Ждем еще немного для полного запуска
sleep 3

# Проверяем доступность сервера
log_info "Проверяем доступность сервера..."
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "Сервер доступен на http://localhost:8000/"
else
    log_error "Сервер недоступен на http://localhost:8000/"
    sudo systemctl status sirius.service
    exit 1
fi

# Проверяем порт
if lsof -ti:8000 > /dev/null 2>&1; then
    log_success "Сервер работает на порту 8000"
else
    log_error "Сервер не работает на порту 8000"
    exit 1
fi

# =============================================================================
# ЭТАП 9: ФИНАЛЬНАЯ ПРОВЕРКА
# =============================================================================
log_info "ЭТАП 9: Финальная проверка..."

# Проверяем логи
log_info "Проверяем логи сервиса..."
sudo journalctl -u sirius.service --no-pager -n 20

# Проверяем процессы
log_info "Проверяем запущенные процессы..."
ps aux | grep -E "(python|uvicorn)" | grep -v grep

# Проверяем порты
log_info "Проверяем открытые порты..."
ss -tlnp | grep :8000

# =============================================================================
# ЗАВЕРШЕНИЕ
# =============================================================================
log_success "=================================================================="
log_success "КОМПЛЕКСНОЕ ОБНОВЛЕНИЕ СЕРВЕРА ЗАВЕРШЕНО УСПЕШНО!"
log_success "=================================================================="
log_success "Сервер доступен по адресу: http://localhost:8000/"
log_success "API документация: http://localhost:8000/docs"
log_success "Статус сервиса: sudo systemctl status sirius.service"
log_success "Логи сервиса: sudo journalctl -u sirius.service -f"
log_success "=================================================================="

# Выводим полезные команды
echo ""
log_info "Полезные команды для управления:"
echo "  Остановить сервер: sudo systemctl stop sirius.service"
echo "  Запустить сервер: sudo systemctl start sirius.service"
echo "  Перезапустить:   sudo systemctl restart sirius.service"
echo "  Статус:          sudo systemctl status sirius.service"
echo "  Логи:            sudo journalctl -u sirius.service -f"
echo "  Остановить автозапуск: sudo systemctl disable sirius.service"
echo ""

log_success "Обновление завершено! 🚀"
