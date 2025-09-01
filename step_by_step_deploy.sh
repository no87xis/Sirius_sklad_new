#!/bin/bash

echo "🚀 Sirius Group - Пошаговое развертывание"
echo "=========================================="
echo "✅ Каждый шаг проверяется перед переходом к следующему"
echo "=========================================="

# Функция для проверки успешности команды
check_step() {
    if [ $? -eq 0 ]; then
        echo "✅ Шаг $1 выполнен успешно"
        return 0
    else
        echo "❌ Шаг $1 НЕ выполнен!"
        echo "🔍 Ошибка на шаге $1. Проверьте логи выше."
        exit 1
    fi
}

# Шаг 1: Остановка процессов
echo "📋 Шаг 1: Остановка процессов..."
pkill -f uvicorn 2>/dev/null || true
pkill -f python 2>/dev/null || true
sleep 3
check_step "1"

# Шаг 2: Очистка
echo "📋 Шаг 2: Очистка старой папки..."
if [ -d "Sirius_sklad_new" ]; then
    rm -rf Sirius_sklad_new
    echo "✅ Старая папка удалена"
else
    echo "✅ Старая папка не найдена"
fi
check_step "2"

# Шаг 3: Клонирование
echo "📋 Шаг 3: Клонирование с GitHub..."
git clone https://github.com/no87xis/Sirius_sklad_new.git
check_step "3"

# Шаг 4: Переход в папку
echo "📋 Шаг 4: Переход в папку проекта..."
cd Sirius_sklad_new
check_step "4"

# Шаг 5: Проверка структуры
echo "📋 Шаг 5: Проверка структуры проекта..."
if [ -f "app/main.py" ] && [ -f "requirements.txt" ]; then
    echo "✅ Структура проекта корректна"
    ls -la
else
    echo "❌ Структура проекта НЕ корректна!"
    echo "📁 Содержимое текущей папки:"
    ls -la
    exit 1
fi
check_step "5"

# Шаг 6: Виртуальное окружение
echo "📋 Шаг 6: Создание виртуального окружения..."
python3 -m venv venv
check_step "6"

# Шаг 7: Активация venv
echo "📋 Шаг 7: Активация виртуального окружения..."
source venv/bin/activate
check_step "7"

# Шаг 8: Установка зависимостей
echo "📋 Шаг 8: Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
check_step "8"

# Шаг 9: Создание .env
echo "📋 Шаг 9: Создание .env файла..."
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
EOF
check_step "9"

# Шаг 10: Создание директорий
echo "📋 Шаг 10: Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads
check_step "10"

# Шаг 11: Диагностика
echo "📋 Шаг 11: Запуск диагностики..."
python3 debug_server.py
check_step "11"

# Шаг 12: Простая инициализация БД
echo "📋 Шаг 12: Инициализация базы данных..."
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    from app.db import Base, engine, SessionLocal
    from app.models.user import User, UserRole
    from app.services.auth import get_password_hash
    
    print('✅ Модули импортированы')
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    print('✅ Таблицы созданы')
    
    # Создаем админа
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                hashed_password=get_password_hash('admin123'),
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print('✅ Админ создан: admin / admin123')
        else:
            print('✅ Админ уже существует')
    finally:
        db.close()
    
    print('✅ База данных готова')
    
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
check_step "12"

# Шаг 13: Тест импорта main.py
echo "📋 Шаг 13: Тест импорта main.py..."
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    from app.main import app
    print('✅ app.main:app импортируется успешно')
    print(f'✅ Тип app: {type(app)}')
except Exception as e:
    print(f'❌ Ошибка импорта: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
check_step "13"

# Шаг 14: Запуск сервера
echo "📋 Шаг 14: Запуск сервера..."
echo "🚀 Запускаем uvicorn с вашим main.py"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
check_step "14"

# Шаг 15: Проверка запуска
echo "📋 Шаг 15: Проверка запуска сервера..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Процесс uvicorn запущен"
else
    echo "❌ Процесс uvicorn НЕ запущен!"
    echo "📋 Лог сервера:"
    tail -20 server.log
    exit 1
fi
check_step "15"

# Шаг 16: Проверка порта
echo "📋 Шаг 16: Проверка порта 8000..."
if netstat -tlnp 2>/dev/null | grep ":8000" > /dev/null; then
    echo "✅ Порт 8000 открыт"
else
    echo "❌ Порт 8000 НЕ открыт!"
    echo "📋 Проверяем процессы:"
    ps aux | grep uvicorn
    exit 1
fi
check_step "16"

# Шаг 17: Тест HTTP запроса
echo "📋 Шаг 17: Тест HTTP запроса..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Сервер отвечает на HTTP запросы"
else
    echo "⚠️ Сервер не отвечает на HTTP запросы"
    echo "📋 Проверяем лог:"
    tail -10 server.log
fi
check_step "17"

echo ""
echo "=========================================="
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!"
echo "=========================================="
echo "🌐 Сайт: http://185.239.50.157:8000"
echo "👤 Админ: admin / admin123"
echo "📋 Лог сервера: tail -f server.log"
echo "🔍 Диагностика: python3 debug_server.py"
echo "=========================================="
