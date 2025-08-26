# Система учёта склада и заказов «Сириус»

Веб-приложение для управления складом, заказами и поставками с разделением ролей пользователей.

## Технологии

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy 2.x + Alembic
- **Auth**: Starlette Sessions + bcrypt
- **UI**: Jinja2 + Tailwind CSS
- **Database**: SQLite (dev), PostgreSQL (prod)

## Установка и запуск

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd sirius_sklad_new
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

```bash
copy env.example .env
# Отредактируйте .env файл, указав свои значения
```

### 5. Инициализация базы данных

```bash
alembic upgrade head
```

### 6. Запуск приложения

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

## Структура проекта

```
sirius/
├─ app/                    # Основное приложение
│  ├─ main.py            # Точка входа FastAPI
│  ├─ config.py          # Конфигурация
│  ├─ db.py              # Настройки базы данных
│  ├─ deps.py            # Зависимости
│  ├─ models/            # Модели данных
│  ├─ schemas/           # Pydantic схемы
│  ├─ services/          # Бизнес-логика
│  ├─ routers/           # Маршруты
│  └─ templates/         # HTML шаблоны
├─ alembic/              # Миграции базы данных
├─ tests/                # Тесты
└─ docs/                 # Документация
```

## Роли пользователей

- **Admin**: Полный доступ ко всем функциям
- **Manager**: Управление товарами, поставками, заказами
- **User**: Просмотр склада, создание и обработка заказов

## API документация

После запуска приложения доступна по адресу: http://localhost:8000/docs

## Разработка

### Создание миграций

```bash
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
```

### Запуск тестов

```bash
pytest
```

## Лицензия

MIT
