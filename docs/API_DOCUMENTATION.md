# План создания API документации (Swagger)

## Обзор

Создание автоматической API документации с использованием FastAPI и Swagger UI для улучшения разработки, тестирования и интеграции.

## Преимущества Swagger

- **Автоматическая генерация**: Документация создается из кода
- **Интерактивное тестирование**: Возможность тестировать API прямо из браузера
- **Стандартизация**: OpenAPI 3.0 стандарт
- **Валидация**: Автоматическая проверка схем данных
- **Клиентская генерация**: Автоматическое создание клиентских библиотек

## Реализация

### 1. Обновление FastAPI приложения

```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Сириус - API Системы учёта склада",
    description="""
    ## Описание
    
    API для управления складом, заказами, товарами и пользователями.
    
    ## Возможности
    
    * 🔐 **Аутентификация и авторизация**
    * 📦 **Управление товарами и складом**
    * 📋 **Создание и управление заказами**
    * 👥 **Управление пользователями**
    * 📊 **Аналитика и отчеты**
    * 🏪 **Магазин и корзина**
    * 📱 **QR-коды и сканирование**
    
    ## Версионирование
    
    Текущая версия: **v1.0.0**
    
    ## Поддержка
    
    Для получения поддержки обращайтесь к администратору системы.
    """,
    version="1.0.0",
    contact={
        "name": "Сириус Групп",
        "email": "support@sirius-group.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS для Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    """Кастомная OpenAPI схема"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Кастомизация схемы
    openapi_schema["info"]["x-logo"] = {
        "url": "https://sirius-group.com/logo.png"
    }
    
    # Добавляем теги
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Аутентификация и авторизация пользователей"
        },
        {
            "name": "products",
            "description": "Управление товарами и складом"
        },
        {
            "name": "orders",
            "description": "Создание и управление заказами"
        },
        {
            "name": "users",
            "description": "Управление пользователями системы"
        },
        {
            "name": "analytics",
            "description": "Аналитика и отчеты"
        },
        {
            "name": "shop",
            "description": "Магазин и корзина покупок"
        },
        {
            "name": "qr",
            "description": "QR-коды и сканирование"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 2. Улучшение схем данных

```python
# schemas/product.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class ProductBase(BaseModel):
    """Базовая схема товара"""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    description: Optional[str] = Field(None, max_length=1000, description="Описание товара")
    quantity: int = Field(..., ge=0, description="Количество на складе")
    min_stock: int = Field(..., ge=0, description="Минимальный остаток")
    buy_price_eur: Decimal = Field(..., ge=0, description="Цена покупки в евро")
    sell_price_rub: Decimal = Field(..., ge=0, description="Цена продажи в рублях")
    supplier_name: Optional[str] = Field(None, max_length=200, description="Название поставщика")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Miele Boost CX1",
                "description": "Мощный пылесос для дома",
                "quantity": 10,
                "min_stock": 2,
                "buy_price_eur": "299.99",
                "sell_price_rub": "29999.00",
                "supplier_name": "Miele Official"
            }
        }
    )

class ProductCreate(ProductBase):
    """Схема для создания товара"""
    pass

class ProductUpdate(BaseModel):
    """Схема для обновления товара"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    quantity: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    buy_price_eur: Optional[Decimal] = Field(None, ge=0)
    sell_price_rub: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = Field(None, max_length=200)

class ProductResponse(ProductBase):
    """Схема ответа для товара"""
    id: int = Field(..., description="Уникальный идентификатор")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")
    photos: List[str] = Field(default=[], description="Список URL фотографий")
    
    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    """Схема ответа для списка товаров"""
    products: List[ProductResponse] = Field(..., description="Список товаров")
    total: int = Field(..., description="Общее количество товаров")
    page: int = Field(..., description="Номер текущей страницы")
    per_page: int = Field(..., description="Количество товаров на странице")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")
```

### 3. Улучшение API endpoints

```python
# routers/api.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from ..services.products import ProductService
from ..services.auth import get_current_user

router = APIRouter()

@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="Получить список товаров",
    description="""
    Получить список товаров с пагинацией и фильтрацией.
    
    **Возможности:**
    * Пагинация результатов
    * Фильтрация по названию
    * Сортировка по различным полям
    * Поиск по описанию
    """,
    tags=["products"],
    responses={
        200: {
            "description": "Список товаров успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "products": [
                            {
                                "id": 1,
                                "name": "Miele Boost CX1",
                                "description": "Мощный пылесос",
                                "quantity": 10,
                                "min_stock": 2,
                                "buy_price_eur": "299.99",
                                "sell_price_rub": "29999.00",
                                "supplier_name": "Miele Official",
                                "created_at": "2024-01-01T10:00:00",
                                "updated_at": "2024-01-01T10:00:00",
                                "photos": []
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "per_page": 20,
                        "has_next": False,
                        "has_prev": False
                    }
                }
            }
        },
        400: {"description": "Некорректные параметры запроса"},
        401: {"description": "Не авторизован"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def get_products(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество товаров на странице"),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    sort_by: str = Query("name", description="Поле для сортировки"),
    sort_order: str = Query("asc", description="Порядок сортировки (asc/desc)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить список товаров с пагинацией и фильтрацией.
    
    - **page**: Номер страницы (начиная с 1)
    - **per_page**: Количество товаров на странице (1-100)
    - **search**: Поисковый запрос
    - **sort_by**: Поле для сортировки
    - **sort_order**: Порядок сортировки
    """
    try:
        products = ProductService(db).get_products(
            page=page,
            per_page=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении товаров: {str(e)}"
        )

@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый товар",
    description="""
    Создать новый товар в системе.
    
    **Требования:**
    * Авторизация администратора или менеджера
    * Все обязательные поля заполнены
    * Корректные значения цен и количества
    """,
    tags=["products"],
    responses={
        201: {
            "description": "Товар успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Новый товар",
                        "description": "Описание товара",
                        "quantity": 100,
                        "min_stock": 10,
                        "buy_price_eur": "50.00",
                        "sell_price_rub": "5000.00",
                        "supplier_name": "Поставщик",
                        "created_at": "2024-01-01T10:00:00",
                        "updated_at": "2024-01-01T10:00:00",
                        "photos": []
                    }
                }
            }
        },
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        422: {"description": "Ошибка валидации"}
    }
)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создать новый товар.
    
    - **product**: Данные товара для создания
    """
    try:
        created_product = ProductService(db).create_product(product, current_user)
        return created_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании товара: {str(e)}"
        )

@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Получить товар по ID",
    description="Получить детальную информацию о товаре по его идентификатору",
    tags=["products"],
    responses={
        200: {"description": "Товар найден"},
        404: {"description": "Товар не найден"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)
async def get_product(
    product_id: int = Path(..., gt=0, description="ID товара"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить товар по ID.
    
    - **product_id**: Уникальный идентификатор товара
    """
    product = ProductService(db).get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    return product
```

### 4. Создание кастомных схем ошибок

```python
# schemas/errors.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    error: str = Field(..., description="Тип ошибки")
    detail: str = Field(..., description="Подробное описание ошибки")
    timestamp: str = Field(..., description="Время возникновения ошибки")
    path: Optional[str] = Field(None, description="Путь запроса")
    method: Optional[str] = Field(None, description="HTTP метод")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "detail": "Поле 'name' обязательно для заполнения",
                "timestamp": "2024-01-01T10:00:00Z",
                "path": "/api/products",
                "method": "POST",
                "user_id": "admin"
            }
        }
    }

class ValidationErrorResponse(ErrorResponse):
    """Схема ошибки валидации"""
    field_errors: Dict[str, str] = Field(..., description="Ошибки по полям")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "detail": "Ошибка валидации данных",
                "timestamp": "2024-01-01T10:00:00Z",
                "path": "/api/products",
                "method": "POST",
                "user_id": "admin",
                "field_errors": {
                    "name": "Поле обязательно для заполнения",
                    "quantity": "Количество должно быть больше 0"
                }
            }
        }
    }
```

### 5. Создание middleware для логирования API

```python
# middleware/api_logging.py
import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..services.logger import logger

class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования API запросов"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Логируем входящий запрос
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "client": request.client.host if request.client else "unknown"
        }
        
        logger.info(f"API Request: {request.method} {request.url.path}", **request_data)
        
        # Обрабатываем запрос
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Логируем успешный ответ
            logger.info(
                f"API Response: {request.method} {request.url.path} - {response.status_code}",
                duration=duration,
                status_code=response.status_code
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Логируем ошибку
            logger.error(
                f"API Error: {request.method} {request.url.path}",
                error=str(e),
                duration=duration,
                **request_data
            )
            raise
```

### 6. Создание тестов для API

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth import create_access_token

client = TestClient(app)

class TestProductsAPI:
    """Тесты для API товаров"""
    
    def test_get_products_unauthorized(self):
        """Тест получения товаров без авторизации"""
        response = client.get("/api/products")
        assert response.status_code == 401
    
    def test_get_products_authorized(self, admin_token):
        """Тест получения товаров с авторизацией"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/products", headers=headers)
        assert response.status_code == 200
        assert "products" in response.json()
    
    def test_create_product_valid(self, admin_token):
        """Тест создания товара с валидными данными"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        product_data = {
            "name": "Тестовый товар",
            "description": "Описание тестового товара",
            "quantity": 100,
            "min_stock": 10,
            "buy_price_eur": "50.00",
            "sell_price_rub": "5000.00",
            "supplier_name": "Тестовый поставщик"
        }
        
        response = client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 201
        assert response.json()["name"] == product_data["name"]
    
    def test_create_product_invalid(self, admin_token):
        """Тест создания товара с невалидными данными"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        product_data = {
            "name": "",  # Пустое название
            "quantity": -1,  # Отрицательное количество
            "buy_price_eur": "-10.00"  # Отрицательная цена
        }
        
        response = client.post("/api/products", json=product_data, headers=headers)
        assert response.status_code == 422
    
    def test_get_product_not_found(self, admin_token):
        """Тест получения несуществующего товара"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/products/99999", headers=headers)
        assert response.status_code == 404

@pytest.fixture
def admin_token():
    """Фикстура для токена администратора"""
    return create_access_token(data={"sub": "admin", "role": "admin"})
```

## Дополнительные возможности

### 1. Автоматическая генерация клиентов

```bash
# Генерация Python клиента
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o python-client

# Генерация JavaScript клиента
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g javascript -o js-client

# Генерация Postman коллекции
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g postman -o postman-collection
```

### 2. Интеграция с CI/CD

```yaml
# .github/workflows/api-docs.yml
name: API Documentation

on:
  push:
    branches: [ main, develop ]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Generate OpenAPI schema
      run: |
        python -c "
        import uvicorn
        from app.main import app
        import json
        
        with open('openapi.json', 'w') as f:
            json.dump(app.openapi(), f, indent=2)
        "
    
    - name: Upload OpenAPI schema
      uses: actions/upload-artifact@v3
      with:
        name: openapi-schema
        path: openapi.json
```

### 3. Мониторинг API

```python
# services/api_monitoring.py
from datetime import datetime, timedelta
from collections import defaultdict
from ..services.logger import logger

class APIMonitor:
    """Мониторинг API endpoints"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Запись метрик запроса"""
        key = f"{method} {endpoint}"
        self.request_counts[key] += 1
        self.response_times[key].append(duration)
        
        if status_code >= 400:
            self.error_counts[key] += 1
        
        # Логируем медленные запросы
        if duration > 1.0:
            logger.warning(f"Медленный API запрос: {key} - {duration:.2f}s")
    
    def get_metrics(self):
        """Получение метрик API"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Вычисляем средние времена ответа
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        return {
            "uptime": str(uptime),
            "total_requests": sum(self.request_counts.values()),
            "request_counts": dict(self.request_counts),
            "avg_response_times": avg_response_times,
            "error_counts": dict(self.error_counts),
            "error_rate": sum(self.error_counts.values()) / max(sum(self.request_counts.values()), 1)
        }
```

## Заключение

Создание качественной API документации с Swagger обеспечит:

1. **Улучшение разработки**: Разработчики смогут легко понимать и тестировать API
2. **Упрощение интеграции**: Клиенты смогут быстро интегрироваться с системой
3. **Стандартизацию**: Следование OpenAPI стандартам
4. **Автоматизацию**: Генерация клиентов и тестов
5. **Мониторинг**: Отслеживание использования и производительности API

Правильная структура и детализация документации значительно улучшат пользовательский опыт и упростят разработку.
