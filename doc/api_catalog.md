# 🔌 Каталог API/маршрутов - Sirius Group

## TL;DR
- **FastAPI backend** с роутерами для разных модулей
- **Shop API** для корзины и заказов
- **Web роутеры** для публичных страниц и админки
- **QR-сканер** и система доставки
- **Swagger документация** на `/docs`

---

## 🌐 Основные роутеры

### **1. Главный роутер (`app/main.py`)**

#### **Подключенные роутеры:**
```python
app.include_router(web_public.router)           # Публичные страницы
app.include_router(web_products.router)         # Управление товарами
app.include_router(web_orders.router)           # Управление заказами
app.include_router(web_analytics.router)        # Аналитика (prefix: /admin)
app.include_router(web_admin_panel.router)      # Админ панель
app.include_router(api.router)                  # API (prefix: /api)
app.include_router(web_shop.router)             # Магазин
app.include_router(shop_api.router)             # Shop API
app.include_router(shop_admin.router)           # Админ магазина
app.include_router(qr_scanner.router)           # QR-сканер
app.include_router(delivery_payment.router)     # Система доставки
```

---

## 🛍️ Shop API (`/api`)

### **Добавление в корзину**
- **Метод**: `POST`
- **Путь**: `/api/shop/cart/add`
- **Файл**: `app/routers/shop_api.py`
- **Параметры**: `product_id`, `quantity`
- **Ответ**: JSON с результатом добавления

### **Добавление в корзину (form data)**
- **Метод**: `POST`
- **Путь**: `/api/shop/cart/add-form`
- **Файл**: `app/routers/shop_api.py`
- **Параметры**: `Form(product_id)`, `Form(quantity)`
- **Ответ**: JSON с результатом добавления
- **Назначение**: Обработка форм для добавления товаров

---

## 🛒 Web Shop (`/shop`)

### **Каталог товаров**
- **Метод**: `GET`
- **Путь**: `/shop/`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `shop_catalog()`
- **Ответ**: HTML страница каталога

### **Страница товара**
- **Метод**: `GET`
- **Путь**: `/shop/product/{product_id}`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `shop_product_detail()`
- **Параметры**: `product_id: int`
- **Ответ**: HTML страница товара

### **Корзина**
- **Метод**: `GET`
- **Путь**: `/shop/cart`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `shop_cart()`
- **Ответ**: HTML страница корзины

### **Добавление в корзину (POST)**
- **Метод**: `POST`
- **Путь**: `/shop/cart/add`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `add_to_cart_post()`
- **Параметры**: `Form(product_id)`, `Form(quantity)`
- **Ответ**: Редирект на корзину

### **Оформление заказа**
- **Метод**: `GET`
- **Путь**: `/shop/checkout`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `shop_checkout()`
- **Ответ**: HTML форма оформления

### **Обработка заказа**
- **Метод**: `POST`
- **Путь**: `/shop/checkout`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `process_checkout()`
- **Параметры**:
  - `Form(customer_name)`
  - `Form(customer_phone)`
  - `Form(customer_city)`
  - `Form(delivery_option)`
  - `Form(delivery_city_other)`
  - `Form(payment_method_id)`
- **Ответ**: Редирект на страницу успеха

### **Страница успешного заказа**
- **Метод**: `GET`
- **Путь**: `/shop/order-success`
- **Файл**: `app/routers/web_shop.py`
- **Функция**: `order_success()`
- **Параметры**: `Query(codes)` - коды заказов
- **Ответ**: HTML страница успеха

---

## 🚚 Система доставки (`/delivery`)

### **Страница оплаты доставки**
- **Метод**: `GET`
- **Путь**: `/delivery/payment`
- **Файл**: `app/routers/delivery_payment.py`
- **Функция**: `delivery_payment_page()`
- **Ответ**: HTML страница с WhatsApp кнопками

### **Страница оплаты доставки (с кодом заказа)**
- **Метод**: `GET`
- **Путь**: `/delivery/payment/{order_code}`
- **Файл**: `app/routers/delivery_payment.py`
- **Функция**: `delivery_payment_with_order()`
- **Параметры**: `order_code: str`
- **Ответ**: HTML страница с информацией о заказе

---

## 🔍 QR-сканер и заказы

### **QR-сканер**
- **Метод**: `GET`
- **Путь**: `/qr-scanner`
- **Файл**: `app/routers/qr_scanner.py`
- **Функция**: `qr_scanner_page()`
- **Ответ**: HTML страница с камерой

### **Поиск заказа**
- **Метод**: `GET`
- **Путь**: `/orders/search`
- **Файл**: `app/routers/web_orders.py`
- **Функция**: `search_order()`
- **Параметры**: `Query(code)`, `Query(phone)`
- **Ответ**: HTML страница заказа или форма поиска

### **Детали заказа**
- **Метод**: `GET`
- **Путь**: `/orders/{order_code}`
- **Файл**: `app/routers/web_orders.py`
- **Функция**: `order_detail()`
- **Параметры**: `order_code: str`
- **Ответ**: HTML страница с деталями заказа

---

## 🏪 Административная часть

### **Главная панель**
- **Метод**: `GET`
- **Путь**: `/admin`
- **Файл**: `app/routers/web_admin_panel.py`
- **Ответ**: HTML админ панель

### **Управление товарами**
- **Метод**: `GET`
- **Путь**: `/admin/products`
- **Файл**: `app/routers/web_products.py`
- **Ответ**: HTML страница управления товарами

### **Управление заказами**
- **Метод**: `GET`
- **Путь**: `/admin/orders`
- **Файл**: `app/routers/web_orders.py`
- **Ответ**: HTML страница управления заказами

### **Аналитика**
- **Метод**: `GET`
- **Путь**: `/admin/analytics`
- **Файл**: `app/routers/web_analytics.py`
- **Ответ**: HTML страница с аналитикой

---

## 📱 Публичные страницы

### **Главная страница**
- **Метод**: `GET`
- **Путь**: `/`
- **Файл**: `app/main.py`
- **Функция**: `root()`
- **Ответ**: HTML главная страница

---

## 🔧 API схемы и документация

### **Swagger UI**
- **Путь**: `/docs`
- **Описание**: Автоматически генерируемая документация API
- **Основа**: FastAPI OpenAPI спецификация

### **OpenAPI JSON**
- **Путь**: `/openapi.json`
- **Описание**: Машиночитаемая спецификация API
- **Использование**: Для генерации клиентов и документации

---

## 📋 Схемы ответов

### **JSON ответы (Shop API)**
```json
{
  "success": true,
  "message": "Товар добавлен в корзину",
  "cart_item_id": 123
}
```

### **HTML ответы**
- **Content-Type**: `text/html`
- **Шаблоны**: Jinja2 templates
- **Базовый шаблон**: `shop/base.html`

---

## 🔍 Чек-лист готовности

- [x] Перечислены все основные роутеры
- [x] Документированы Shop API endpoints
- [x] Описаны Web Shop маршруты
- [x] Документирована система доставки
- [x] Описаны QR-сканер и заказы
- [x] Перечислены административные маршруты
- [x] Указаны файлы реализации
- [x] Описаны схемы ответов
- [x] Документирована Swagger документация

---

*Документ создан на основе статического анализа роутеров*





