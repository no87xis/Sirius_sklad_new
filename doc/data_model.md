# 🗄️ Модель данных и связи - Sirius Group

## TL;DR
- **SQLite база данных** с таблицами для заказов, товаров, пользователей
- **Система доставки** с новыми полями в таблице orders
- **QR-коды** для каждого заказа с уникальными токенами
- **Сессионная корзина** с временным хранением товаров
- **Модели SQLAlchemy** с валидацией и связями

---

## 📊 Таблицы/модели

### **1. Таблица `orders` (Заказы)**

#### **Основные поля:**
- `id` - первичный ключ (INTEGER, PRIMARY KEY)
- `phone` - телефон клиента (STRING, NOT NULL, INDEX)
- `customer_name` - имя клиента (STRING, NULLABLE)
- `client_city` - город клиента (STRING(100), NULLABLE)
- `product_id` - ID товара (INTEGER, FOREIGN KEY)
- `product_name` - название товара (STRING, NULLABLE) - денормализация
- `qty` - количество (INTEGER, NOT NULL)
- `unit_price_rub` - цена за единицу (NUMERIC(10,2), NOT NULL)
- `eur_rate` - курс евро (NUMERIC(10,4), DEFAULT 0)

#### **Система оплаты:**
- `order_code` - уникальный код заказа (STRING(8), UNIQUE, INDEX)
- `order_code_last4` - последние 4 символа кода (STRING(4), INDEX)
- `payment_method_id` - ID способа оплаты (INTEGER, FOREIGN KEY)
- `payment_instrument_id` - ID инструмента оплаты (INTEGER, FOREIGN KEY)
- `paid_amount` - оплаченная сумма (NUMERIC(10,2), NULLABLE)
- `paid_at` - время оплаты (DATETIME, NULLABLE)

#### **Старые поля (совместимость):**
- `payment_method` - способ оплаты (ENUM: 'card', 'cash', 'unpaid', 'other')
- `payment_note` - заметка по оплате (STRING(120), NULLABLE)
- `status` - статус заказа (ENUM: 'PAID_NOT_ISSUED', 'PAID_ISSUED', 'PAID_DENIED')
- `created_at` - время создания (DATETIME, DEFAULT NOW)
- `issued_at` - время выдачи (DATETIME, NULLABLE)
- `user_id` - ID пользователя (STRING, FOREIGN KEY)

#### **Источник заказа:**
- `source` - источник заказа (STRING(20), DEFAULT 'manual') - 'manual' или 'shop'

#### **QR-код поля:**
- `qr_payload` - уникальный токен для QR-кода (STRING, NULLABLE, INDEX)
- `qr_image_path` - путь к изображению QR-кода (STRING, NULLABLE)
- `qr_generated_at` - время генерации QR-кода (DATETIME, NULLABLE)

#### **Поля системы доставки:**
- `delivery_option` - тип доставки (STRING(50), NULLABLE, INDEX)
- `delivery_city_other` - город для "Другая (по согласованию)" (STRING(100), NULLABLE)
- `delivery_unit_price_rub` - тариф за единицу (INTEGER, DEFAULT 300)
- `delivery_units` - количество единиц для расчета (INTEGER, NULLABLE)
- `delivery_cost_rub` - итоговая стоимость доставки (INTEGER, NULLABLE)
- `delivery_payment_enabled` - оплата доставки включена (STRING(5), DEFAULT "FALSE")

#### **Индексы:**
- `phone` - для поиска по телефону
- `order_code` - для поиска по коду заказа
- `order_code_last4` - для быстрого поиска по последним символам
- `payment_method_id` - для фильтрации по способу оплаты
- `status` - для фильтрации по статусу
- `user_id` - для поиска заказов пользователя
- `qr_payload` - для поиска по QR-коду
- `delivery_option` - для фильтрации по типу доставки

---

### **2. Таблица `products` (Товары)**

#### **Основные поля:**
- `id` - первичный ключ (INTEGER, PRIMARY KEY)
- `name` - название товара (STRING, NOT NULL)
- `description` - описание (TEXT, NULLABLE)
- `sell_price_rub` - цена продажи (NUMERIC(10,2), NOT NULL)
- `buy_price_rub` - цена закупки (NUMERIC(10,2), NULLABLE)
- `quantity` - количество на складе (INTEGER, DEFAULT 0)
- `category` - категория товара (STRING, NULLABLE)
- `created_at` - время создания (DATETIME, DEFAULT NOW)
- `updated_at` - время обновления (DATETIME, DEFAULT NOW)

#### **Связи:**
- `orders` - заказы с этим товаром (relationship)

---

### **3. Таблица `users` (Пользователи)**

#### **Основные поля:**
- `username` - имя пользователя (STRING, PRIMARY KEY)
- `password_hash` - хеш пароля (STRING, NOT NULL)
- `role` - роль пользователя (STRING, NOT NULL)
- `created_at` - время создания (DATETIME, DEFAULT NOW)
- `last_login` - последний вход (DATETIME, NULLABLE)

#### **Связи:**
- `orders` - заказы пользователя (relationship)

---

### **4. Таблица `shop_cart` (Корзина магазина)**

#### **Основные поля:**
- `id` - первичный ключ (INTEGER, PRIMARY KEY)
- `session_id` - ID сессии (STRING, NOT NULL, INDEX)
- `product_id` - ID товара (INTEGER, FOREIGN KEY)
- `quantity` - количество (INTEGER, NOT NULL, DEFAULT 1)
- `created_at` - время создания (DATETIME, DEFAULT NOW)
- `updated_at` - время обновления (DATETIME, DEFAULT NOW)

#### **Индексы:**
- `session_id` - для поиска товаров в корзине сессии

---

### **5. Таблица `payment_methods` (Способы оплаты)**

#### **Основные поля:**
- `id` - первичный ключ (INTEGER, PRIMARY KEY)
- `name` - название способа (STRING, NOT NULL)
- `description` - описание (TEXT, NULLABLE)
- `fee_percent` - процент комиссии (NUMERIC(5,2), DEFAULT 0)
- `is_active` - активен ли способ (BOOLEAN, DEFAULT TRUE)

#### **Связи:**
- `orders` - заказы с этим способом оплаты (relationship)

---

## 🔗 Связи между таблицами

### **Основные связи:**
```python
# Order -> Product
order.product = relationship("Product", back_populates="orders")

# Order -> User  
order.user = relationship("User", back_populates="orders")

# Order -> PaymentMethod
order.payment_method_rel = relationship("PaymentMethod", back_populates="orders")

# Product -> Orders
product.orders = relationship("Order", back_populates="product")

# User -> Orders
user.orders = relationship("Order", back_populates="user")
```

---

## 📋 Enum значения

### **OrderStatus (Статусы заказов):**
```python
class OrderStatus(str, enum.Enum):
    PAID_NOT_ISSUED = "paid_not_issued"  # Оплачен, не выдан
    PAID_ISSUED = "paid_issued"          # Оплачен и выдан
    PAID_DENIED = "paid_denied"          # Оплачен, но отказано
```

### **PaymentMethod (Способы оплаты - старые):**
```python
class PaymentMethod(str, enum.Enum):
    CARD = "card"        # Картой
    CASH = "cash"        # Наличными
    UNPAID = "unpaid"    # Не оплачен
    OTHER = "other"      # Другое
```

### **DeliveryOption (Варианты доставки):**
```python
class DeliveryOption(str, enum.Enum):
    SELF_PICKUP_GROZNY = "SELF_PICKUP_GROZNY"  # Самовывоз (Склад, Грозный)
    COURIER_GROZNY = "COURIER_GROZNY"           # Доставка в Грозный
    COURIER_MAK = "COURIER_MAK"                 # Доставка в Махачкалу
    COURIER_KHAS = "COURIER_KHAS"               # Доставка в Хасавюрт
    COURIER_OTHER = "COURIER_OTHER"             # Другой город
```

---

## 🎯 Использование полей в UI

### **order.code:**
- **Отображается**: на странице успешного заказа, в деталях заказа
- **Используется**: для поиска заказа, QR-кода, ссылок

### **order.status:**
- **Отображается**: как кнопка "Не оплачено" (клиент) или "ВЫДАНО/НЕ ВЫДАНО" (менеджер)
- **Используется**: для блокировки действий, смены статуса

### **order.delivery_option:**
- **Отображается**: в форме checkout как select с вариантами
- **Используется**: для расчета стоимости доставки, показа/скрытия полей

### **order.delivery_cost_rub:**
- **Отображается**: в сводке заказа как "Доставка: X ₽"
- **Используется**: для расчета итоговой суммы

### **product.quantity:**
- **Отображается**: в каталоге как "В наличии: X шт."
- **Используется**: для проверки доступности товара

---

## 📊 Mermaid ER диаграмма

```mermaid
erDiagram
    USERS ||--o{ ORDERS : "создает"
    PRODUCTS ||--o{ ORDERS : "включает"
    PAYMENT_METHODS ||--o{ ORDERS : "использует"
    SHOP_CART ||--o{ PRODUCTS : "содержит"
    
    USERS {
        string username PK
        string password_hash
        string role
        datetime created_at
        datetime last_login
    }
    
    ORDERS {
        int id PK
        string phone
        string customer_name
        string client_city
        int product_id FK
        string product_name
        int qty
        numeric unit_price_rub
        string order_code UK
        int payment_method_id FK
        enum status
        datetime created_at
        string delivery_option
        int delivery_cost_rub
        string qr_payload
    }
    
    PRODUCTS {
        int id PK
        string name
        text description
        numeric sell_price_rub
        int quantity
        string category
    }
    
    PAYMENT_METHODS {
        int id PK
        string name
        numeric fee_percent
        boolean is_active
    }
    
    SHOP_CART {
        int id PK
        string session_id
        int product_id FK
        int quantity
        datetime created_at
    }
```

---

## 🔍 Чек-лист готовности

- [x] Описаны все основные таблицы
- [x] Перечислены поля с типами и ограничениями
- [x] Документированы индексы и уникальные ограничения
- [x] Описаны Enum значения статусов
- [x] Показаны связи между таблицами
- [x] Создана ER диаграмма
- [x] Описано использование полей в UI
- [x] Документирована система доставки

---

*Документ создан на основе статического анализа моделей*





