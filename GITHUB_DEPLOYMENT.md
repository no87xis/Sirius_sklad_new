# 🚀 Полная инструкция по развертыванию Sirius Group

## ✅ ВСЕ ПРОБЛЕМЫ РЕШЕНЫ!

Все критические проблемы исправлены и функционал полностью восстановлен:

### 🔧 Исправленные проблемы:
- ✅ **Проблема с `payment_method` constraint** - исправлена миграцией
- ✅ **Проблема с `order status` constraint** - исправлена миграцией  
- ✅ **Создание заказов из корзины** - работает корректно
- ✅ **Статусы товаров** - отображаются правильно
- ✅ **Сервер стабилен** - не падает при запуске
- ✅ **QR-коды** - добавлены поля в модель Order
- ✅ **Страница успешного оформления** - полностью восстановлена
- ✅ **Недостающие зависимости** - добавлены pydantic-settings, itsdangerous, qrcode, pillow
- ✅ **Проблемы с Python3** - исправлены скрипты развертывания

### 🎯 Восстановленный функционал:
- ✅ **Заказы из магазина видны в админке** в разделе заказов
- ✅ **Страница успешного оформления** с полным функционалом:
  - ✅ Код заказа с кнопкой копирования
  - ✅ QR-код с возможностью скачивания
  - ✅ Ссылка на заказ с кнопкой копирования
  - ✅ Текст для WhatsApp с кнопкой копирования
  - ✅ Прямые ссылки на WhatsApp менеджеров
  - ✅ Информация о резерве товаров
  - ✅ Форма поиска заказа

## 📋 Быстрое развертывание

### 1. Сохраните код на GitHub
```bash
git add .
git commit -m "🚀 Sirius Group - исправлены проблемы с Python3 и инициализацией БД"
git push origin master
```

### 2. На сервере выполните:

#### Linux/Mac сервер:
```bash
# Клонируем репозиторий
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new

# Запускаем автоматическое развертывание
chmod +x deploy.sh
./deploy.sh

# Запускаем сервер
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Windows сервер:
```cmd
# Клонируем репозиторий
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new

# Запускаем автоматическое развертывание
deploy.bat

# Запускаем сервер
venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Если возникли проблемы на сервере:

### Быстрое исправление:
```bash
# В папке Sirius_sklad_new
chmod +x fix_server.sh
./fix_server.sh
```

### Ручное исправление:
```bash
# 1. Остановите сервер
pkill -f uvicorn

# 2. Перейдите в папку проекта
cd Sirius_sklad_new

# 3. Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Создайте .env файл
cat > .env << EOF
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=app/static/uploads
MAX_FILE_SIZE=10485760
EOF

# 6. Создайте папки
mkdir -p app/static/uploads app/static/qr logs

# 7. Инициализируйте базу данных
python3 -c "
from app.db import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ База данных инициализирована')
"

# 8. Примените миграции
alembic upgrade head

# 9. Запустите сервер
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📊 Перенос базы данных (ОПЦИОНАЛЬНО)

Если хотите перенести данные с локальной машины на сервер:

### 1. На локальной машине:
```bash
# Linux/Mac
./transfer_db.sh

# Windows
transfer_db.bat
```

### 2. Загрузите БД на сервер:
```bash
scp sirius_sklad.db root@your-server-ip:/root/
```

### 3. На сервере:
```bash
cd /root/sirius-project/Sirius_sklad_new
cp /root/sirius_sklad.db .
chown www-data:www-data sirius_sklad.db  # если используете nginx
chmod 644 sirius_sklad.db

# Перезапустите сервер
pkill -f uvicorn
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## ⚡ Быстрое развертывание (с потерей данных)

Если нужно быстро развернуть без сохранения старых данных:

```bash
# 1. Остановите старый сервер
pkill -f uvicorn

# 2. Удалите старую папку
rm -rf sirius_sklad_new

# 3. Клонируйте заново
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new

# 4. Запустите развертывание
./deploy.sh  # Linux/Mac
# или
deploy.bat   # Windows

# 5. Запустите сервер
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Что было исправлено

### 1. **Проблема с payment_method**
- **Проблема:** `CHECK constraint failed: payment_method IN ('card', 'cash', 'unpaid', 'other')`
- **Решение:** Создана миграция для исправления типа поля с `String` на `Enum`
- **Результат:** Заказы создаются корректно

### 2. **Проблема с order status**
- **Проблема:** `CHECK constraint failed: status IN ('paid_not_issued', 'paid_issued', 'paid_denied')`
- **Решение:** Создана миграция для исправления типа поля с `String` на `Enum`
- **Результат:** Статусы заказов работают правильно

### 3. **Проблема с сервером**
- **Проблема:** Сервер падал при запуске
- **Решение:** Исправлен `app/main.py` - убраны проблемные lifespan события
- **Результат:** Сервер запускается стабильно

### 4. **Восстановление QR-функционала**
- **Проблема:** QR-коды не работали для заказов из магазина
- **Решение:** Добавлены QR-поля в модель Order, обновлен QR-сервис
- **Результат:** QR-коды генерируются и отображаются корректно

### 5. **Восстановление страницы успешного оформления**
- **Проблема:** Страница не находила заказы после изменения логики
- **Решение:** Обновлен поиск заказов в таблице Order, исправлен шаблон
- **Результат:** Полный функционал страницы восстановлен

### 6. **Недостающие зависимости**
- **Проблема:** `ModuleNotFoundError: No module named 'pydantic_settings'` и `'itsdangerous'`
- **Решение:** Добавлены в requirements.txt и скрипты развертывания
- **Результат:** Сервер запускается без ошибок

### 7. **Проблемы с Python3 на сервере**
- **Проблема:** `python: command not found`, `venv/bin/activate: No such file or directory`
- **Решение:** Исправлены скрипты для использования `python3` и правильной инициализации БД
- **Результат:** Развертывание работает на всех серверах

## 🌐 Доступные страницы

- **Админка:** `http://your-server-ip:8000/`
- **Магазин:** `http://your-server-ip:8000/shop`
- **API документация:** `http://your-server-ip:8000/docs`

## 🔐 Стандартные учетные данные

- **Админ:** `admin` / `admin123`
- **Менеджер:** `manager` / `manager123`

## 📝 Проверка работоспособности

После развертывания проверьте:

1. **Создание товара:** `http://your-server-ip:8000/products/new`
2. **Создание заказа:** `http://your-server-ip:8000/orders/new`
3. **Магазин:** `http://your-server-ip:8000/shop`
4. **Корзина:** Добавьте товар в корзину и оформите заказ
5. **Страница успешного оформления:** Проверьте все функции:
   - Копирование кода заказа
   - Скачивание QR-кода
   - Копирование ссылки на заказ
   - Копирование текста для WhatsApp
   - Ссылки на WhatsApp менеджеров

## ⚠️ Важные замечания

1. **Измените SECRET_KEY** в .env файле для продакшена
2. **Настройте файрвол** для доступа к порту 8000
3. **Используйте nginx** для проксирования на порт 80/443
4. **Настройте SSL** для HTTPS в продакшене

## 🎉 Готово!

**Система Sirius Group полностью готова к работе! 🚀**

Все критические ошибки исправлены, сервер стабилен, заказы создаются корректно, 
QR-коды работают, страница успешного оформления восстановлена со всем функционалом!
