# 🚀 Операционный гид - Sirius Group

## 📋 Быстрый старт

### **Запуск dev-сервера:**
```cmd
scripts\win\make.bat up
```

### **Проверка статуса:**
```cmd
scripts\win\make.bat status
```

### **Просмотр логов:**
```cmd
scripts\win\make.bat logs
```

### **Остановка сервера:**
```cmd
scripts\win\make.bat down
```

---

## 🚫 Что Cursor НЕ делает

- ❌ **НЕ запускает** долгоживущие процессы через `run_terminal_cmd`
- ❌ **НЕ запускает** серверы (`uvicorn`, `gunicorn`, `nginx`)
- ❌ **НЕ запускает** процессы с `--reload` или `--watch`
- ❌ **НЕ выполняет** интерактивные команды

**Все серверы запускаются ТОЛЬКО через `scripts\win\make.bat up`**

---

## 📁 Логи и диагностика

### **Где искать логи:**
- `logs\uvicorn-dev.log` - основные логи сервера
- `logs\uvicorn-dev.pid` - PID файл процесса
- `logs\uvicorn-dev.out` - stdout сервера
- `logs\uvicorn-dev.err` - stderr сервера

### **Как читать логи:**
```cmd
# Последние 20 строк
scripts\win\make.bat logs

# В реальном времени
powershell Get-Content logs\uvicorn-dev.log -Wait -Tail 10

# Все логи
type logs\uvicorn-dev.log
```

### **Проверка процессов:**
```cmd
# Процессы Python
tasklist | findstr python

# Порт 8000
netstat -an | findstr :8000
```

---

## 🔍 Опциональные проверки

### **Health endpoints:**
```cmd
# Корневой health endpoint
curl http://127.0.0.1:8000/health

# API health endpoint  
curl http://127.0.0.1:8000/api/health
```

**Ожидаемый ответ:**
```json
{"status": "ok"}
```

### **Проверка доступности:**
- ✅ **HTTP 200 OK** - сервер работает
- ✅ **JSON ответ** - приложение отвечает
- ❌ **Connection refused** - сервер не запущен
- ❌ **Timeout** - сервер завис

### **Интеграция в скрипты:**
В `scripts/win/serve_status.cmd` есть закомментированная опция для автоматической проверки `/health` endpoint. Для включения раскомментируйте соответствующие строки.

---

## 🚨 Troubleshooting

### **Сервер не запускается:**
1. **Проверить порт:** `netstat -an | findstr :8000`
2. **Очистить PID:** `del logs\uvicorn-dev.pid`
3. **Закрыть зависшие процессы:** `taskkill /f /im python.exe`
4. **Перезапуск:** `scripts\win\make.bat up`

### **Сервер завис:**
1. **Остановка:** `scripts\win\make.bat down`
2. **Принудительная остановка:** `taskkill /f /im python.exe`
3. **Очистка PID:** `del logs\uvicorn-dev.pid`
4. **Перезапуск:** `scripts\win\make.bat up`

### **Ошибки зависимостей:**
1. **Переустановка:** `pip install -r requirements.txt --force-reinstall`
2. **Пересоздание venv:** `rmdir /s venv && python -m venv venv`
3. **Активация:** `venv\Scripts\activate`

### **Проблемы с кодировкой:**
1. **Проверить настройки терминала**
2. **Убедиться, что ConPTY отключен**
3. **Перезапустить Cursor**

---

## 📋 Чек-лист тестирования

**Используйте `doc/terminal_stability_tests.md` как полный чек-лист для:**
- Быстрых проверок из Cursor
- Ручных проверок во внешнем терминале
- Критериев успеха
- Устранения проблем

---

## 🎯 Основные команды

| **Действие** | **Команда** |
|--------------|-------------|
| Сборка проекта | `scripts\win\make.bat` |
| Запуск сервера | `scripts\win\make.bat up` |
| Проверка статуса | `scripts\win\make.bat status` |
| Просмотр логов | `scripts\win\make.bat logs` |
| Остановка сервера | `scripts\win\make.bat down` |
| Проверка порта | `netstat -an | findstr :8000` |
| Проверка процессов | `tasklist | findstr python` |
| Принудительная остановка | `taskkill /f /im python.exe` |

---

**Дата создания:** 3 сентября 2025  
**Версия:** 1.0  
**Статус:** Активен
