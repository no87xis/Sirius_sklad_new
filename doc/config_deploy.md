# ⚙️ Конфигурация и деплой - Sirius Group

## TL;DR
- **FastAPI backend** с uvicorn на порту 8000
- **SQLite база данных** в `app/database/sirius.db`
- **Jinja2 templates** + Tailwind CSS для фронтенда
- **PowerShell скрипты** для Windows деплоя
- **Система доставки** с миграциями БД

---

## 🔧 Конфигурация приложения

### **Основные файлы конфигурации:**

#### **1. `app/config.py`**
```python
# Основные настройки приложения
SECRET_KEY = "your-secret-key-here"
DATABASE_URL = "sqlite:///app/database/sirius.db"
SESSION_MAX_AGE = 86400  # 24 часа
```

#### **2. `app/db.py`**
```python
# Настройки базы данных
DATABASE_URL = "sqlite:///app/database/sirius.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

#### **3. `requirements.txt`**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
jinja2==3.1.2
python-multipart==0.0.6
```

---

## 🚀 Запуск сервиса

### **Политика запуска процессов в dev: только через scripts/win**

**⚠️ КРИТИЧЕСКИ ВАЖНО:** В режиме разработки все долгоживущие процессы (серверы, uvicorn, gunicorn) запускаются **ТОЛЬКО** через специальные скрипты в папке `scripts/win/`. Cursor сам **НИКОГДА** не запускает долгоживущие процессы через `run_terminal_cmd`.

#### **Разрешенные способы запуска:**
- ✅ `scripts\win\serve_dev.cmd` - запуск dev-сервера
- ✅ `scripts\win\make.bat` - сборка проекта
- ✅ Ручной запуск скриптов пользователем

#### **Запрещенные способы:**
- ❌ `run_terminal_cmd` с uvicorn/gunicorn
- ❌ `run_terminal_cmd` с процессами `--reload`
- ❌ `run_terminal_cmd` с любыми долгоживущими процессами

#### **Проверка статуса:**
- ✅ Чтение логов: `type logs\uvicorn-dev.log`
- ✅ Команды status: `scripts\win\serve_status.cmd`
- ✅ Короткие команды: `netstat -an | findstr :8000`
- ❌ НЕ через `run_terminal_cmd` для долгоживущих процессов

### **Локальная разработка:**
```bash
# 1. Сборка проекта
scripts\win\make.bat

# 2. Запуск dev-сервера
scripts\win\serve_dev.cmd

# 3. Проверка статуса
scripts\win\serve_status.cmd

# 4. Остановка сервера
scripts\win\serve_stop.cmd
```

### **Продакшн:**
```bash
# Запуск без reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Параметры запуска:**
- **Хост**: `0.0.0.0` (доступ извне)
- **Порт**: `8000`
- **Workers**: 4 (для продакшна)
- **Reload**: только для разработки

---

## 🗄️ База данных

### **Тип БД:**
- **SQLite** - встроенная база данных
- **Файл**: `app/database/sirius.db`
- **Размер**: ~208KB (текущий)

### **Создание таблиц:**
```python
# В app/main.py
Base.metadata.create_all(bind=engine)
```

### **Миграции:**
- **Файл**: `migrations/add_delivery_system.py`
- **Назначение**: Добавление полей системы доставки
- **Безопасность**: Проверка существования полей перед добавлением

### **⚠️ Важно для read-only анализа:**
```bash
# Создание копии БД для анализа
cp app/database/sirius.db /tmp/sirius_analysis.db

# Анализ схемы
sqlite3 /tmp/sirius_analysis.db ".schema"
```

---

## 📁 Структура проекта

### **Основные директории:**
```
Sirius_sklad_new/
├── app/                    # Основной код приложения
│   ├── main.py           # Точка входа FastAPI
│   ├── config.py         # Конфигурация
│   ├── db.py             # База данных
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── routers/          # FastAPI роутеры
│   ├── services/         # Бизнес-логика
│   ├── templates/        # Jinja2 шаблоны
│   ├── static/           # Статические файлы
│   └── constants/        # Константы (доставка)
├── migrations/            # Миграции БД
├── venv/                 # Виртуальное окружение
├── requirements.txt       # Python зависимости
└── *.ps1                 # PowerShell скрипты
```

---

## 🖥️ Системные требования

### **Операционная система:**
- **Windows 10/11** (основная)
- **PowerShell 5.1+** для скриптов
- **Python 3.8+** для приложения

### **Зависимости:**
- **Python**: 3.8, 3.9, 3.10, 3.11
- **pip**: для установки пакетов
- **Git**: для управления версиями

### **Порты:**
- **8000**: основное приложение (uvicorn)
- **80/443**: веб-сервер (если используется nginx)

---

## 📜 PowerShell скрипты

### **1. `run_diagnosis.ps1`**
- **Назначение**: Диагностика системы
- **Действия**: проверка файлов, импортов, БД
- **Запуск**: `.\run_diagnosis.ps1`

### **2. `start_server.ps1`**
- **Назначение**: Запуск сервера
- **Действия**: активация venv, установка зависимостей, запуск uvicorn
- **Запуск**: `.\start_server.ps1`

### **3. `diagnose_and_fix.py`**
- **Назначение**: Python диагностика
- **Действия**: проверка компонентов, миграции
- **Запуск**: `python diagnose_and_fix.py`

---

## 🔒 Безопасность

### **Переменные окружения:**
```bash
# .env файл (не коммитить в Git!)
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///app/database/sirius.db
DEBUG=False
```

### **Секретные ключи:**
- **SECRET_KEY**: для сессий и JWT токенов
- **DATABASE_URL**: строка подключения к БД
- **DEBUG**: режим отладки (False для продакшна)

### **⚠️ Что категорически нельзя делать в проде:**
- Запускать миграции без резервной копии БД
- Использовать `--reload` флаг
- Оставлять DEBUG=True
- Использовать простые SECRET_KEY
- Открывать порт 8000 в файрволе без необходимости

---

## 📊 Мониторинг и логи

### **Логи uvicorn:**
```bash
# Просмотр логов
uvicorn app.main:app --log-level info

# Логи в файл
uvicorn app.main:app --log-config logging.conf
```

### **Логи приложения:**
- **Файл**: `logs/app.log` (если настроено)
- **Уровень**: INFO, WARNING, ERROR
- **Ротация**: по размеру или времени

### **Метрики:**
- **Порт**: проверка `netstat -an | findstr :8000`
- **Процесс**: `tasklist | findstr uvicorn`
- **Память**: `wmic process where name="python.exe" get WorkingSetSize`

---

## 🚨 Устранение неполадок

### **Проблема: "Address already in use"**
```bash
# Поиск процесса на порту 8000
netstat -ano | findstr :8000

# Завершение процесса
taskkill /PID <PID> /F
```

### **Проблема: "Module not found"**
```bash
# Активация виртуального окружения
& "venv\Scripts\Activate.ps1"

# Установка зависимостей
pip install -r requirements.txt
```

### **Проблема: "Database locked"**
```bash
# Проверка процессов SQLite
tasklist | findstr sqlite

# Перезапуск приложения
# (SQLite автоматически освобождает блокировки)
```

---

## 🔄 Деплой на сервер

### **Подготовка:**
1. **Клонирование репозитория**
2. **Создание виртуального окружения**
3. **Установка зависимостей**
4. **Настройка .env файла**

### **Запуск:**
1. **Диагностика**: `.\run_diagnosis.ps1`
2. **Запуск сервера**: `.\start_server.ps1`
3. **Проверка**: `curl http://localhost:8000`

### **Обновление:**
1. **Git pull** последних изменений
2. **Перезапуск** сервера
3. **Проверка** работоспособности

---

## 📋 Чек-лист готовности

- [x] Описаны основные файлы конфигурации
- [x] Документированы параметры запуска
- [x] Описана структура базы данных
- [x] Перечислены системные требования
- [x] Документированы PowerShell скрипты
- [x] Описаны меры безопасности
- [x] Документирован мониторинг
- [x] Описано устранение неполадок
- [x] Документирован процесс деплоя

---

*Документ создан на основе статического анализа конфигурации*





