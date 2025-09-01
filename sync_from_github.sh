#!/bin/bash

echo "🔄 Sirius Group - Синхронизация с GitHub"
echo "========================================"

# 1. Проверка подключения к GitHub
echo "📋 1. Проверка подключения к GitHub..."
if ! git ls-remote --exit-code origin >/dev/null 2>&1; then
    echo "❌ Ошибка подключения к GitHub"
    echo "Проверьте интернет-соединение и доступность репозитория"
    exit 1
fi

# 2. Переход в папку проекта
echo "📋 2. Переход в проект..."
cd ~/Sirius_sklad_new

# 3. Проверка статуса git
echo "📋 3. Проверка статуса Git..."
git status --porcelain

# 4. Сохранение локальных изменений (если есть)
echo "📋 4. Сохранение локальных изменений..."
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Обнаружены локальные изменения"
    echo "Сохранение в stash..."
    git stash push -m "Автоматическое сохранение перед обновлением $(date)"
fi

# 5. Получение информации об обновлениях
echo "📋 5. Проверка обновлений..."
git fetch origin

# Получаем информацию о последних коммитах
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/master)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ Код уже актуален, обновлений нет"
    echo "Локальный коммит: ${LOCAL_COMMIT:0:8}"
    echo "Удаленный коммит: ${REMOTE_COMMIT:0:8}"
else
    echo "🔄 Обнаружены обновления!"
    echo "Локальный коммит: ${LOCAL_COMMIT:0:8}"
    echo "Удаленный коммит: ${REMOTE_COMMIT:0:8}"
    
    # Показываем что изменилось
    echo "📝 Последние изменения:"
    git log --oneline HEAD..origin/master
    
    # 6. Обновление кода
    echo "📋 6. Обновление кода..."
    git reset --hard origin/master
    echo "✅ Код обновлен до последней версии"
fi

# 7. Остановка сервера
echo "📋 7. Остановка сервера..."
pkill -f uvicorn
sleep 3

# 8. Активация окружения
echo "📋 8. Активация окружения..."
source venv/bin/activate

# 9. Обновление зависимостей
echo "📋 9. Обновление зависимостей..."
pip install -r requirements.txt

# 10. Применение миграций
echo "📋 10. Применение миграций..."
alembic upgrade head

# 11. Запуск сервера
echo "📋 11. Запуск сервера..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 12. Проверка статуса
echo "📋 12. Проверка статуса..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен успешно!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
    echo "📋 Лог: tail -f server.log"
    
    # Показываем информацию о версии
    echo "📊 Информация о версии:"
    echo "Коммит: $(git rev-parse --short HEAD)"
    echo "Дата: $(git log -1 --format=%cd)"
    echo "Автор: $(git log -1 --format=%an)"
    echo "Сообщение: $(git log -1 --format=%s)"
else
    echo "❌ Ошибка запуска сервера"
    echo "📋 Проверьте лог:"
    tail -20 server.log
fi

echo "========================================"
echo "🎉 Синхронизация завершена!"
