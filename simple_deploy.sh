#!/bin/bash

echo "🚀 Sirius Group - Простое развертывание"
echo "========================================"
echo "✅ Берем рабочий код и запускаем на сервере"
echo "✅ Никаких изменений, никаких костылей"
echo "========================================"

# 1. Остановка процессов
echo "📋 1. Остановка процессов..."
pkill -f uvicorn
pkill -f python
sleep 3

# 2. Очистка
echo "📋 2. Очистка..."
rm -rf Sirius_sklad_new
echo "✅ Старая папка удалена"

# 3. Клонирование
echo "📋 3. Клонирование..."
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new
echo "✅ Код загружен"

# 4. Виртуальное окружение
echo "📋 4. Виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Виртуальное окружение создано"

# 5. Зависимости
echo "📋 5. Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# 6. Конфигурация
echo "📋 6. Конфигурация..."
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
EOF

# 7. Директории
echo "📋 7. Создание директорий..."
mkdir -p static/uploads/products
mkdir -p static/uploads/qr
chmod -R 755 static/uploads

# 8. ПРОСТАЯ инициализация базы данных
echo "📋 8. Инициализация базы данных..."
echo "🔧 Создаем таблицы и админа..."

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

if [ $? -ne 0 ]; then
    echo "❌ Ошибка инициализации базы данных"
    exit 1
fi

# 9. Запуск сервера
echo "📋 9. Запуск сервера..."
echo "🚀 Запускаем ваш рабочий main.py"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 10. Проверка
echo "📋 10. Проверка..."
sleep 5

if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер запущен!"
    echo "🌐 Сайт: http://185.239.50.157:8000"
    echo "👤 Админ: admin / admin123"
    echo "📋 Лог: tail -f server.log"
else
    echo "❌ Ошибка запуска"
    echo "📋 Лог:"
    tail -20 server.log
    exit 1
fi

echo "========================================"
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "🚀 Сервер работает с вашим кодом"
echo "✅ Никаких изменений, никаких костылей"
echo "========================================"
