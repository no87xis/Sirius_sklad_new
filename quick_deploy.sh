#!/bin/bash

# =============================================================================
# БЫСТРЫЙ ДЕПЛОЙ SIRIUS GROUP
# =============================================================================
# Простой скрипт для быстрого обновления кода без перезапуска сервисов
# =============================================================================

set -e

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "Использование: $0 <путь_к_проекту> [branch_name]"
    echo "Пример: $0 /home/user/sirius main"
    exit 1
fi

PROJECT_PATH="$1"
BRANCH="${2:-main}"

cd "$PROJECT_PATH"

log_info "Быстрое обновление Sirius Group..."
log_info "Путь: $PROJECT_PATH"
log_info "Ветка: $BRANCH"

# Сохраняем изменения
git stash push -m "Quick update $(date)" || true

# Обновляем код
git checkout "$BRANCH"
git fetch origin
git reset --hard "origin/$BRANCH"

# Очищаем файлы
git clean -fd

log_success "Код обновлен!"

# Проверяем сервис
if systemctl is-active --quiet sirius.service; then
    log_info "Перезапускаем сервис..."
    sudo systemctl restart sirius.service
    
    # Ждем запуска
    sleep 3
    
    if systemctl is-active --quiet sirius.service; then
        log_success "Сервис перезапущен успешно!"
    else
        log_warning "Ошибка перезапуска сервиса"
        sudo systemctl status sirius.service
    fi
else
    log_warning "Сервис sirius.service не запущен"
fi

log_success "Быстрое обновление завершено! 🚀"
