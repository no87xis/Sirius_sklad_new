# 🚀 Финальная инструкция по развертыванию Sirius Group

## ✅ Проблемы решены

Все критические проблемы исправлены:
- ✅ **Проблема с `payment_method` constraint** - исправлена миграцией
- ✅ **Проблема с `order status` constraint** - исправлена миграцией  
- ✅ **Создание заказов из корзины** - работает корректно
- ✅ **Статусы товаров** - отображаются правильно
- ✅ **Сервер стабилен** - не падает при запуске

## 📋 Быстрое развертывание

### 1. Сохраните код на GitHub
```bash
git add .
git commit -m "🚀 Sirius Group - исправлены все критические ошибки"
git push origin main
```

### 2. На сервере выполните:

#### Linux/Mac сервер:
```bash
# Клонируем репозиторий
git clone <your-github-repo-url>
cd sirius_sklad_new

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
git clone <your-github-repo-url>
cd sirius_sklad_new

# Запускаем автоматическое развертывание
deploy.bat

# Запускаем сервер
venv\Scripts\activate.bat
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
git clone <your-github-repo-url>
cd sirius_sklad_new

# 4. Запустите развертывание
./deploy.sh  # Linux/Mac
# или
deploy.bat   # Windows

# 5. Запустите сервер
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Что исправлено

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

## ⚠️ Важные замечания

1. **Измените SECRET_KEY** в .env файле для продакшена
2. **Настройте файрвол** для доступа к порту 8000
3. **Используйте nginx** для проксирования на порт 80/443
4. **Настройте SSL** для HTTPS в продакшене

## 🎉 Готово!

Система Sirius Group полностью готова к работе! 🚀

Все критические ошибки исправлены, сервер стабилен, заказы создаются корректно.
