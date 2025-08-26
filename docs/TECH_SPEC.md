ТЗ: Система учёта склада и заказов «Сириус»
1) Цель и ключевые сценарии

Цель: простой и надёжный учёт товаров, заказов и поставок, с разделением ролей и удобной веб-админкой.
Роли и сценарии:

Admin: управление пользователями и ролями, товарами, поставками, заказами, просмотр логов и аналитики.

Manager (опционально, как под-админ): управление товарами/поставками/заказами, без управления пользователями.

User (оператор): видеть и обрабатывать все заказы (изменять статус: «выдано»), видеть склад, создавать заказы.

2) Технологический стек

Backend: FastAPI (Python 3.11+), SQLAlchemy 2.x, Alembic (миграции)

Auth: сессии Starlette (SessionMiddleware), bcrypt/passlib для паролей

DB: SQLite (dev), PostgreSQL (prod)

UI: Jinja2 + Tailwind CSS; без SPA на старте

Админка: кастомные шаблоны Jinja2 (единый стиль), без сторонней авто-админки

Уведомления: Telegram (через Bot API), опционально Email (SMTP)

Логи: OperationLog в БД

Тесты: pytest

Документация: Swagger (/docs), Markdown в README.md и docs/

3) Архитектура и структура проекта (новый чистый репозиторий)
sirius/
├─ app/
│  ├─ main.py                 # FastAPI приложение, маршруты и точка входа
│  ├─ deps.py                 # зависимости (current_user, require_role, get_db)
│  ├─ config.py               # чтение .env (SECRET_KEY, DB_URL, TELEGRAM_TOKEN, и т.д.)
│  ├─ db.py                   # создание engine, SessionLocal, Base
│  ├─ models/
│  │  ├─ __init__.py          # экспорт моделей
│  │  ├─ user.py              # User
│  │  ├─ product.py           # Product
│  │  ├─ order.py             # Order
│  │  └─ supply.py            # Supply (поставки)
│  │  └─ operation_log.py     # OperationLog (аудит)
│  ├─ schemas/
│  │  ├─ auth.py              # Pydantic схемы login/register
│  │  ├─ product.py
│  │  ├─ order.py
│  │  └─ supply.py
│  ├─ services/
│  │  ├─ auth.py              # хэширование пароля, проверка, смена
│  │  ├─ notifications.py     # Telegram/email
│  │  └─ analytics.py         # агрегации и отчёты
│  ├─ routers/
│  │  ├─ web_public.py        # главная, логин/регистрация, мои заказы (UI)
│  │  ├─ web_admin.py         # админские UI-страницы (пользователи, склад, заказы, логи, аналитика)
│  │  └─ api.py               # REST API (товары/заказы/поставки)
│  ├─ templates/
│  │  ├─ base.html            # общий сайт (верхнее меню, футер)
│  │  ├─ admin/base_admin.html# общий админ-шаблон (боковое меню)
│  │  ├─ index.html
│  │  ├─ login.html
│  │  ├─ register.html
│  │  ├─ my_orders.html
│  │  ├─ admin/users.html
│  │  ├─ admin/products.html
│  │  ├─ admin/orders.html
│  │  ├─ admin/supplies.html
│  │  └─ admin/analytics.html
│  └─ static/
│     └─ tailwind.css
├─ alembic/                   # миграции
├─ tests/                     # pytest
├─ .env.example
├─ requirements.txt
├─ .gitignore
├─ README.md
└─ docs/
   └─ TECH_SPEC.md

4) Модель данных
4.1 User

username (PK, str)

hashed_password (str)

role (enum: admin/manager/user; по умолчанию user)

created_at (datetime)

4.2 Product

id (PK, int)

name (str, уникальное)

description (nullable)

Учётные поля:

quantity (int) — общий приход (сумма поставок)

min_stock (int, default=0) — порог низкого остатка

buy_price_eur (Decimal/Float, nullable) — входная цена (евро)

sell_price_rub (Decimal/Float, nullable) — плановая розничная цена (руб)

supplier_name (str, nullable) — поставщик

Вычисляемые:

stock = quantity − сумма выданных/зарезервированных по заказам

is_low_stock = stock < min_stock

4.3 Supply (Поставка)

id (PK)

product_id (FK → Product)

qty (int, >0)

supplier_name (str)

buy_price_eur (Decimal/Float)

created_at (datetime)

При создании Supply увеличиваем product.quantity и логируем событие.

4.4 Order

id (PK)

phone (str, обязателен)

customer_name (str, nullable)

product_id (FK → Product)

product_name (денормализация для истории, nullable)

qty (int, >0)

unit_price_rub (Decimal/Float) — цена продажи на момент заказа (можно редактировать)

status (enum): paid_not_issued, paid_issued, paid_denied

created_at (datetime), issued_at (nullable)

user_id (FK → User.username) — кто создал/обновил

Проверка наличия stock на момент «оплаты/резерва» (в рамках выбранной бизнес-логики). При «выдано» — уменьшаем склад.

4.5 OperationLog

id, timestamp, user_id (nullable),
action (str), entity_type (str), entity_id (str/int), details (JSON/text)

5) Бизнес-логика и правила доступа

Роли и доступ:

/admin/** — только admin (и опционально manager, если включим).

Склад (просмотр) — user/admin/manager.

Создание/редактирование товаров, поставок — admin/manager.

Заказы:

Все пользователи (включая user) видят все заказы и могут менять статус на «выдано».

Создание заказа — user/admin/manager.

API зеркалирует те же правила.

Stock/quantity: quantity хранится, stock вычисляемый (не хранится). Выдача заказа уменьшает фактический остаток (через суммарную модель: quantity − выдано).

Скидки: при создании заказа unit_price_rub подтягивается из продукта, но может быть изменён вручную (скидки). В заказе хранится цена на момент продажи.

Уведомления: при product.stock < min_stock — локальный лог + отправка в Telegram администратору (если настроены переменные среды).

Логи: все операции (создание/редактирование/выдача/отмена/поставка/изменение ролей) пишутся в OperationLog.

6) Веб-интерфейсы (UI)
6.1 Общий вид

Единый стиль (Tailwind).

Верхнее меню: Главная, Склад, Заказы, Аналитика, справа — Вход/Регистрация или «Привет, username (role)» и Выход.

Никаких «мигающих» ссылок: простые hover-состояния без сдвигов/анимаций.

6.2 Главная (/)

Три карточки-ссылки:

Управление складом → /products

Обработка заказов → /orders

Аналитика → /admin/analytics (пока заглушка «в разработке»)

Баннер для уведомлений (успех/ошибка) через query-param.

6.3 Склад (/products)

Таблица товаров (name, stock, min_stock, цены, поставщик).

Кнопка «Добавить товар» (модалка/страница):

Поля: name, description, supplier_name, buy_price_eur, sell_price_rub, начальный приход qty (необязательно).

Дата создаётся автоматически.

Просмотр и редактирование товара (изменение цен, min_stock, supplier_name).

История поставок товара (линк на supplies).

Поставки (/supplies):

Форма: product (select), qty, supplier_name, buy_price_eur.

Добавление увеличивает product.quantity и пишет лог.

6.4 Заказы (/orders)

Кнопка «Добавить заказ»:

Поля: phone (обязателен), customer_name (nullable), product (select из склада), qty, unit_price_rub (предзаполнена из товара, но редактируема), статус (paid_not_issued — по умолчанию).

Таблица: ID, дата, товар, qty, цена, сумма, телефон, статус.

Сортировки: по телефону, статусу, дате.

Действия по каждой строке: «Выдать», «Отменить» (меняют статус; «выдать» фиксирует выдачу и уменьшает остаток).

(Позже) QR-сканирование для поиска заказа.

6.5 Аналитика (/admin/analytics)

MVP:

Продажи за день/неделю/месяц (шт и ₽)

Разбивка по товарам (шт, сумма)

Доходность (сумма(продаж) − сумма(вход))

Фильтры: по датам, по товару.

Экспорт CSV.

6.6 Админка (/admin/...)

Пользователи: список, назначение роли admin/user, удаление (нельзя удалить себя).

Логи операций: таблица с фильтрами по дате/пользователю/типу действия.

7) API (минимальный набор)

POST /api/auth/register — регистрация.

POST /api/auth/login — вход (устанавливает сессию), POST /logout — выход.

GET /api/products, POST /api/products, PUT /api/products/{id}, DELETE /api/products/{id}

GET /api/products/{id}/stock — текущий остаток (computed)

POST /api/supplies — добавить поставку

GET /api/orders, POST /api/orders, PUT /api/orders/{id}, POST /api/orders/{id}/issue, POST /api/orders/{id}/deny

GET /api/analytics/summary?from=&to=&product_id=

Все эндпоинты зеркалируют правила ролей.

8) Уведомления

Telegram:
ENV: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.
События:

Низкий остаток продукта (при создании/редактировании/поставке/выдаче, если stock < min_stock).

Изменение статуса заказа (опционально).

Локальные баннеры на UI: через query-params (?success=...&error=...).

9) Миграции и БД

Alembic настроен с target_metadata из app.db.Base.

Скрипты:

alembic revision --autogenerate -m "...", alembic upgrade head

В DEV — SQLite, в PROD — PostgreSQL.

.env:
DATABASE_URL, SECRET_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SESSION_MAX_AGE

10) Безопасность

Пароли — bcrypt (passlib).

Секреты и ключи — только в .env (не коммитим).

Rate limiting для /login (позже).

CSP/XSS — на проде (позже).

Отмена авто-индексации /admin (robots), заголовки безопасности (позже).

11) Тестирование (pytest)

Юнит-тесты: модели и сервисы (auth, analytics).

Интеграционные: заказы/поставки/скидки, вычисление stock, смена статусов.

E2E (минимум): регистрация, вход, добавление товара, заказ, выдача.

12) Дорожная карта (этапы)

Этап 0: Бутстрап репозитория

Создать структуру папок, README.md, .gitignore, requirements.txt, .env.example.

Alembic init.

Готовность: uvicorn app.main:app --reload поднимается, / открывается.

Этап 1: Пользователи и сессии

Регистрация, вход/выход, роли.

Верхнее меню корректно показывает статус входа.

DoD: вход работает, роли проверяются, ссылки без «мигания».

Этап 2: Склад

Модель Product, Supply, вычисление stock, min_stock.

UI: добавление/редактирование товара, добавление поставок, таблицы.

Уведомления о low stock (лог + Telegram).

DoD: можно завести товары и поставки, остаток считается.

Этап 3: Заказы

Создание заказа (select товара, qty, редактируемая цена).

Таблица заказов, сортировки, статусы, «Выдать/Отменить».

Корректная корректировка остатка при выдаче.

DoD: полный цикл «товар → заказ → выдача».

Этап 4: Аналитика

Агрегации (день/неделя/месяц), по товару, доходность.

Экспорт CSV.

DoD: отчёты выводятся, экспорт работает.

Этап 5: Админка и логи

Пользователи (смена ролей, удаление), OperationLog с фильтрами.

DoD: все операции пишутся в лог, админ видит и управляет.

Этап 6: Полировка

Уведомления/баннеры, адаптив, мелкие UX-исправления.

Документация, демо-данные (populate).

DoD: аккуратный интерфейс, описание для команды, скрипты демо-данных.

13) Оптимизация UX/визуала

Убрать «мигание» ссылок — простые hover-состояния Tailwind (hover:bg-gray-100 и т.п.), без трансформаций/анимаций, которые меняют размеры.

Карточки главной — сделать ссылками (<a> с блоковой версткой), наведение — мягкая тень.

Единая сетка и отступы (контейнер, max-w-7xl).

Баннеры для успеха/ошибки — единый компонент.

14) Критерии приёмки (Definition of Done)

Репозиторий чистый: нет __pycache__, .sqlite3 в Git.

README.md описывает запуск локально и миграции.

Все вышеописанные страницы работают; роли и доступ корректны.

Заказ оформляется и выдаётся, склад корректно уменьшается.

Уведомления low stock и логи работают.

Тесты проходят локально (pytest -q) хотя бы на MVP-наборе.