# 🚀 ИНСТРУКЦИЯ ПО ДЕПЛОЮ SIRIUS GROUP НА СЕРВЕР

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### На сервере должны быть установлены:
- **Git** - для получения кода
- **Python 3.8+** - для запуска приложения
- **pip** - для установки зависимостей
- **curl** - для проверки работоспособности
- **lsof** - для проверки портов
- **sudo** - для управления сервисами

### Проверка установки:
```bash
# Проверяем версии
python3 --version
pip --version
git --version

# Проверяем наличие утилит
which curl
which lsof
which sudo
```

## 🔧 УСТАНОВКА И НАСТРОЙКА

### 1. Клонирование проекта:
```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем проект
git clone https://github.com/your-username/sirius-group.git
cd sirius-group

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения:
```bash
# Создаем файл .env
cp .env.example .env

# Редактируем настройки
nano .env
```

**Основные настройки в .env:**
```env
# База данных
DATABASE_URL=sqlite:///./app/database/sirius.db

# Безопасность
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки сервера
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 🚀 ЗАПУСК СЕРВЕРА

### Вариант 1: Комплексное обновление (рекомендуется для первого запуска)

```bash
# Делаем скрипт исполняемым
chmod +x update_server_complete.sh

# Запускаем комплексное обновление
./update_server_complete.sh /home/user/sirius-group main
```

**Что делает комплексное обновление:**
1. ✅ Останавливает все старые сервисы
2. ✅ Создает резервную копию БД
3. ✅ Обновляет код из Git
4. ✅ Обновляет зависимости
5. ✅ Инициализирует базу данных
6. ✅ Создает systemd сервис
7. ✅ Запускает сервер
8. ✅ Проверяет работоспособность

### Вариант 2: Быстрое обновление (для обновления кода)

```bash
# Делаем скрипт исполняемым
chmod +x quick_deploy.sh

# Запускаем быстрое обновление
./quick_deploy.sh /home/user/sirius-group main
```

**Что делает быстрое обновление:**
1. ✅ Обновляет код из Git
2. ✅ Перезапускает сервис
3. ✅ Проверяет статус

## 📊 УПРАВЛЕНИЕ СЕРВИСОМ

### Основные команды:
```bash
# Статус сервиса
sudo systemctl status sirius.service

# Запуск сервиса
sudo systemctl start sirius.service

# Остановка сервиса
sudo systemctl stop sirius.service

# Перезапуск сервиса
sudo systemctl restart sirius.service

# Включение автозапуска
sudo systemctl enable sirius.service

# Отключение автозапуска
sudo systemctl disable sirius.service
```

### Просмотр логов:
```bash
# Логи в реальном времени
sudo journalctl -u sirius.service -f

# Последние 50 строк логов
sudo journalctl -u sirius.service -n 50

# Логи за определенную дату
sudo journalctl -u sirius.service --since "2024-01-01"
```

## 🔍 ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### 1. Проверка статуса сервиса:
```bash
sudo systemctl status sirius.service
```

### 2. Проверка портов:
```bash
# Проверяем, что порт 8000 открыт
ss -tlnp | grep :8000

# Или используем lsof
lsof -i :8000
```

### 3. Проверка доступности:
```bash
# Проверяем главную страницу
curl http://localhost:8000/

# Проверяем API документацию
curl http://localhost:8000/docs

# Проверяем статус API
curl http://localhost:8000/health
```

### 4. Проверка процессов:
```bash
# Ищем процессы Python
ps aux | grep python

# Ищем процессы uvicorn
ps aux | grep uvicorn
```

## 🛠️ УСТРАНЕНИЕ ПРОБЛЕМ

### Проблема: Порт 8000 занят
```bash
# Находим процесс
lsof -ti:8000

# Убиваем процесс
kill -9 $(lsof -ti:8000)

# Или перезапускаем сервис
sudo systemctl restart sirius.service
```

### Проблема: Сервис не запускается
```bash
# Проверяем логи
sudo journalctl -u sirius.service -n 50

# Проверяем статус
sudo systemctl status sirius.service

# Проверяем конфигурацию
sudo systemctl cat sirius.service
```

### Проблема: Ошибки в базе данных
```bash
# Проверяем права доступа
ls -la app/database/

# Пересоздаем базу (осторожно!)
rm app/database/sirius.db
python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('База данных пересоздана')
"
```

### Проблема: Зависимости не установлены
```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Переустанавливаем зависимости
pip install -r requirements.txt --force-reinstall
```

## 📁 СТРУКТУРА ПРОЕКТА

```
sirius-group/
├── app/                    # Основной код приложения
│   ├── main.py            # Точка входа
│   ├── database.py        # Настройки БД
│   ├── models/            # Модели данных
│   ├── routers/           # Маршруты API
│   ├── services/          # Бизнес-логика
│   └── templates/         # HTML шаблоны
├── venv/                  # Виртуальное окружение
├── requirements.txt        # Зависимости Python
├── .env                   # Переменные окружения
├── update_server_complete.sh  # Комплексное обновление
├── quick_deploy.sh        # Быстрое обновление
└── DEPLOY_INSTRUCTIONS.md # Эта инструкция
```

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации:
1. **Измените SECRET_KEY** в файле .env
2. **Настройте firewall** для ограничения доступа
3. **Используйте HTTPS** в продакшене
4. **Регулярно обновляйте** зависимости
5. **Мониторьте логи** на подозрительную активность

### Firewall (Ubuntu/Debian):
```bash
# Устанавливаем ufw
sudo apt install ufw

# Разрешаем SSH
sudo ufw allow ssh

# Разрешаем HTTP (опционально)
sudo ufw allow 80

# Разрешаем HTTPS (рекомендуется)
sudo ufw allow 443

# Включаем firewall
sudo ufw enable
```

## 📈 МОНИТОРИНГ

### Автоматический перезапуск:
Сервис настроен на автоматический перезапуск при сбоях:
- `Restart=always` - всегда перезапускается
- `RestartSec=10` - ждет 10 секунд перед перезапуском

### Проверка здоровья:
```bash
# Создайте cron задачу для проверки
crontab -e

# Добавьте строку (проверка каждые 5 минут)
*/5 * * * * curl -f http://localhost:8000/health || sudo systemctl restart sirius.service
```

## 🎯 ЧАСТЫЕ СЦЕНАРИИ

### Первый запуск на новом сервере:
```bash
# 1. Клонируем проект
git clone https://github.com/your-username/sirius-group.git
cd sirius-group

# 2. Запускаем комплексное обновление
chmod +x update_server_complete.sh
./update_server_complete.sh /home/user/sirius-group main
```

### Обновление кода:
```bash
# Быстрое обновление
./quick_deploy.sh /home/user/sirius-group main
```

### Перезапуск сервера:
```bash
sudo systemctl restart sirius.service
```

### Проверка статуса:
```bash
sudo systemctl status sirius.service
```

## 📞 ПОДДЕРЖКА

### Полезные команды для диагностики:
```bash
# Общая информация о системе
uname -a
df -h
free -h

# Информация о Python
python3 --version
pip list

# Информация о Git
git status
git log --oneline -10

# Информация о сервисах
systemctl list-units --type=service | grep sirius
```

### Логи и отладка:
```bash
# Логи systemd
sudo journalctl -u sirius.service -f

# Логи приложения (если настроены)
tail -f /var/log/sirius/app.log

# Проверка конфигурации
sudo systemctl cat sirius.service
```

---

## 🎉 ПОЗДРАВЛЯЕМ!

Если вы дочитали до конца этой инструкции, значит вы готовы к деплою! 

**Удачи с запуском Sirius Group! 🚀**

---

*Последнее обновление: $(date)*
