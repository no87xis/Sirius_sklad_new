# 🚀 Инструкция по развертыванию Sirius Group

## Быстрое развертывание (рекомендуется)

### Linux/Mac
```bash
# 1. Клонируем репозиторий
git clone <your-repo-url>
cd sirius_sklad_new

# 2. Запускаем скрипт развертывания
chmod +x deploy.sh
./deploy.sh

# 3. Запускаем сервер
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Windows
```cmd
# 1. Клонируем репозиторий
git clone <your-repo-url>
cd sirius_sklad_new

# 2. Запускаем скрипт развертывания
deploy.bat

# 3. Запускаем сервер
venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Ручное развертывание

### 1. Подготовка системы
```bash
# Установка Python 3.8+ (если не установлен)
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-venv python3-pip

# CentOS/RHEL:
sudo yum install python3 python3-pip

# Windows: скачайте с python.org
```

### 2. Клонирование и настройка
```bash
# Клонируем репозиторий
git clone <your-repo-url>
cd sirius_sklad_new

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate.bat  # Windows

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Настройка окружения
```bash
# Создаем .env файл
cp .env.example .env

# Редактируем .env (ОБЯЗАТЕЛЬНО измените SECRET_KEY!)
nano .env  # Linux/Mac
# или
notepad .env  # Windows
```

### 4. Инициализация базы данных
```bash
# Применяем миграции
alembic upgrade head
```

### 5. Создание папок
```bash
# Создаем необходимые папки
mkdir -p app/static/uploads
mkdir -p logs
```

### 6. Запуск сервера
```bash
# Режим разработки
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Продакшн режим
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Настройка для продакшена

### 1. Изменение .env файла
```env
DATABASE_URL=sqlite:///./sirius_sklad.db
SECRET_KEY=your-super-secure-secret-key-32-chars-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=app/static/uploads
MAX_FILE_SIZE=10485760
```

### 2. Настройка systemd (Linux)
```bash
# Создаем сервис
sudo nano /etc/systemd/system/sirius.service
```

```ini
[Unit]
Description=Sirius Group Warehouse System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/sirius_sklad_new
Environment=PATH=/path/to/sirius_sklad_new/venv/bin
ExecStart=/path/to/sirius_sklad_new/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Активируем сервис
sudo systemctl daemon-reload
sudo systemctl enable sirius
sudo systemctl start sirius
```

### 3. Настройка nginx (опционально)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/sirius_sklad_new/app/static/;
    }
}
```

## Проверка развертывания

### 1. Проверка сервера
```bash
# Проверяем статус
curl http://localhost:8000/

# Проверяем API
curl http://localhost:8000/docs
```

### 2. Проверка базы данных
```bash
# Проверяем миграции
alembic current
alembic history
```

### 3. Проверка логов
```bash
# Просмотр логов
tail -f logs/app.log

# Проверка systemd логов (если используется)
sudo journalctl -u sirius -f
```

## Устранение проблем

### Сервер не запускается
1. Проверьте, что виртуальное окружение активировано
2. Проверьте, что все зависимости установлены
3. Проверьте .env файл
4. Проверьте логи

### Ошибки базы данных
1. Удалите старую базу данных: `rm sirius_sklad.db`
2. Примените миграции заново: `alembic upgrade head`

### Проблемы с правами доступа
```bash
# Установите правильные права
sudo chown -R www-data:www-data /path/to/sirius_sklad_new
sudo chmod -R 755 /path/to/sirius_sklad_new
```

## Обновление системы

### 1. Остановка сервера
```bash
# Если используете systemd
sudo systemctl stop sirius

# Или остановите процесс вручную
pkill -f uvicorn
```

### 2. Обновление кода
```bash
# Получаем обновления
git pull origin main

# Обновляем зависимости
pip install -r requirements.txt

# Применяем миграции
alembic upgrade head
```

### 3. Запуск сервера
```bash
# Запускаем заново
sudo systemctl start sirius
```

## Резервное копирование

### База данных
```bash
# Создание бэкапа
cp sirius_sklad.db sirius_sklad_backup_$(date +%Y%m%d_%H%M%S).db

# Восстановление
cp sirius_sklad_backup_YYYYMMDD_HHMMSS.db sirius_sklad.db
```

### Загруженные файлы
```bash
# Создание бэкапа
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz app/static/uploads/

# Восстановление
tar -xzf uploads_backup_YYYYMMDD_HHMMSS.tar.gz
```
