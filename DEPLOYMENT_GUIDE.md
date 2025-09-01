# 🚀 Sirius Group - Руководство по развертыванию

## 📋 Системные требования

- Ubuntu 22.04 LTS
- Python 3.10+
- Git
- Nginx (опционально для прокси)

## 🔧 Первоначальная установка

### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и Git
sudo apt install python3 python3-venv python3-pip git -y
```

### 2. Клонирование и установка
```bash
# Клонирование репозитория
cd ~
git clone https://github.com/no87xis/Sirius_sklad_new.git
cd Sirius_sklad_new

# Запуск полной установки
chmod +x update_server.sh
./update_server.sh
```

## ⚡ Быстрое обновление

### Для обновления кода без переустановки:
```bash
cd ~/Sirius_sklad_new
chmod +x quick_update.sh
./quick_update.sh
```

### Для полного обновления с нуля:
```bash
cd ~/Sirius_sklad_new
chmod +x update_server.sh
./update_server.sh
```

## 🔄 Автоматические обновления

### Настройка автоматического обновления:
```bash
# Создание cron задачи для ежедневного обновления
crontab -e

# Добавить строку:
0 2 * * * cd /root/Sirius_sklad_new && ./quick_update.sh >> /var/log/sirius_update.log 2>&1
```

## 🛠️ Управление сервером

### Запуск сервера:
```bash
cd ~/Sirius_sklad_new
source venv/bin/activate
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### Остановка сервера:
```bash
pkill -f uvicorn
```

### Проверка статуса:
```bash
ps aux | grep uvicorn
tail -f server.log
```

### Просмотр логов:
```bash
tail -f server.log
```

## 🗄️ Управление базой данных

### Создание резервной копии:
```bash
cp sirius_sklad.db sirius_sklad_backup_$(date +%Y%m%d_%H%M%S).db
```

### Восстановление из резервной копии:
```bash
cp sirius_sklad_backup_YYYYMMDD_HHMMSS.db sirius_sklad.db
```

### Создание админа вручную:
```bash
cd ~/Sirius_sklad_new
source venv/bin/activate
python3 -c "
from app.db import SessionLocal
from app.models import User
from app.services.auth import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@sirius.com',
    hashed_password=get_password_hash('admin123'),
    is_active=True,
    is_superuser=True
)
db.add(admin)
db.commit()
print('✅ Админ создан: admin / admin123')
db.close()
"
```

## 🔍 Диагностика проблем

### Проверка статуса сервера:
```bash
# Проверка процессов
ps aux | grep uvicorn

# Проверка портов
netstat -tlnp | grep 8000

# Проверка логов
tail -f server.log
```

### Проверка базы данных:
```bash
# Проверка файла БД
ls -la sirius_sklad.db

# Проверка таблиц
sqlite3 sirius_sklad.db ".tables"
```

### Проверка зависимостей:
```bash
source venv/bin/activate
pip list
```

## 🚨 Решение частых проблем

### 1. Сервер не запускается
```bash
# Проверка логов
tail -f server.log

# Перезапуск с полной установкой
./update_server.sh
```

### 2. Не работает вход в админку
```bash
# Пересоздание админа
python3 -c "
from app.db import SessionLocal
from app.models import User
from app.services.auth import get_password_hash

db = SessionLocal()
db.query(User).filter(User.username == 'admin').delete()
admin = User(
    username='admin',
    email='admin@sirius.com',
    hashed_password=get_password_hash('admin123'),
    is_active=True,
    is_superuser=True
)
db.add(admin)
db.commit()
print('✅ Админ пересоздан: admin / admin123')
db.close()
"
```

### 3. Старая версия отображается
```bash
# Очистка кэша nginx
sudo systemctl reload nginx
sudo rm -rf /var/cache/nginx/*

# Перезапуск сервера
pkill -f uvicorn
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

## 📞 Контакты и поддержка

- **Логин админа**: admin / admin123
- **Порт сервера**: 8000
- **URL сайта**: http://185.239.50.157:8000

## 📝 Примечания

1. Все скрипты автоматически создают админа
2. База данных сохраняется при обновлениях
3. Логи сохраняются в `server.log`
4. Резервные копии создаются автоматически

## 🔄 План будущих обновлений

1. **Автоматические бэкапы** - ежедневное создание резервных копий
2. **Мониторинг** - автоматическая проверка статуса сервера
3. **Уведомления** - оповещения о проблемах
4. **Откат версий** - возможность быстрого отката к предыдущей версии
