# 🚀 Развертывание Sirius Group на сервере

## 📋 Что нужно сделать

### 1. Сохраните код на GitHub
```bash
# Добавьте все файлы в git
git add .

# Создайте коммит
git commit -m "🚀 Sirius Group - готовая система управления складом"

# Отправьте на GitHub
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

## 🔧 Что включено в развертывание

✅ **Автоматическая установка зависимостей**  
✅ **Создание виртуального окружения**  
✅ **Настройка .env файла**  
✅ **Применение миграций базы данных**  
✅ **Создание необходимых папок**  
✅ **Настройка прав доступа**  

## 🌐 Доступные страницы после развертывания

- **Админка:** `http://your-server-ip:8000/`
- **Магазин:** `http://your-server-ip:8000/shop`
- **API документация:** `http://your-server-ip:8000/docs`

## 🔐 Стандартные учетные данные

- **Админ:** `admin` / `admin123`
- **Менеджер:** `manager` / `manager123`

## ⚠️ Важные замечания

1. **Измените SECRET_KEY** в .env файле для продакшена
2. **Настройте файрвол** для доступа к порту 8000
3. **Используйте nginx** для проксирования на порт 80/443
4. **Настройте SSL** для HTTPS в продакшене

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f logs/app.log`
2. Проверьте статус сервера: `curl http://localhost:8000/`
3. Проверьте базу данных: `alembic current`

## 🎉 Готово!

Система Sirius Group готова к работе! 🚀
