# 🚨 Быстрый чек-лист исправления проблем

## ❌ Сервер не запускается?

### 1. Проверьте виртуальное окружение
```bash
# Должно быть (venv) в начале строки
(venv) PS D:\Sirius_sklad_new>

# Если нет - активируйте:
venv\Scripts\activate
```

### 2. Проверьте зависимости
```bash
python -c "import fastapi; print('OK')"
```

### 3. Проверьте конфигурацию
```bash
# Создайте .env если его нет
copy env.example .env
```

### 4. Проверьте базу данных
```bash
alembic current
```

### 5. Запустите диагностику
```bash
python test_server_debug.py
```

## 🚀 Быстрый запуск

### Windows (CMD)
```bash
start_server.bat
```

### Windows (PowerShell)
```bash
.\start_server.ps1
```

### Ручной запуск
```bash
venv\Scripts\activate
python test_server_debug.py
```

## 🔍 Частые ошибки

| Ошибка | Решение |
|--------|---------|
| `No module named 'fastapi'` | Активируйте venv |
| `ImportError` | Проверьте синтаксис |
| `Port in use` | Измените порт на 8001 |
| `Database error` | Проверьте миграции |

## 📞 Экстренная помощь

1. **Запустите диагностику**: `python test_server_debug.py`
2. **Проверьте логи**: папка `logs/`
3. **Создайте issue** с описанием ошибки
