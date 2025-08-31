# План интеграции Redis для кэширования

## Обзор

Redis будет использоваться для кэширования часто запрашиваемых данных, сессий и временных данных, что значительно улучшит производительность системы.

## Преимущества Redis

- **Скорость**: Операции в памяти (микросекунды)
- **Гибкость**: Различные типы данных (строки, хеши, списки, множества)
- **Надежность**: Персистентность и репликация
- **Масштабируемость**: Кластеризация и шардинг
- **Функциональность**: TTL, транзакции, Lua скрипты

## Архитектура кэширования

### Уровни кэширования

1. **L1 - Кэш приложения** (in-memory)
   - Кэширование объектов в памяти процесса
   - Быстрый доступ, но ограниченный объем

2. **L2 - Redis кэш**
   - Централизованное кэширование
   - Общий доступ для всех экземпляров приложения
   - Персистентность данных

3. **L3 - База данных**
   - Основное хранилище данных
   - Медленный доступ, но полные данные

### Стратегии кэширования

1. **Cache-Aside (Lazy Loading)**
   - Приложение проверяет кэш перед обращением к БД
   - Если данных нет в кэше, загружает из БД и сохраняет в кэш

2. **Write-Through**
   - При записи данных обновляется и БД, и кэш
   - Обеспечивает консистентность данных

3. **Write-Back**
   - Данные сначала записываются в кэш
   - Периодически синхронизируются с БД

## Реализация

### 1. Установка зависимостей

```txt
# requirements.txt
redis==5.0.1
hiredis==4.2.0  # Ускоренный парсер Redis
```

### 2. Конфигурация Redis

```python
# config.py
class Settings(BaseSettings):
    # Redis настройки
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_max_connections: int = 20
    
    # Кэширование
    cache_ttl_default: int = 3600  # 1 час
    cache_ttl_short: int = 300     # 5 минут
    cache_ttl_long: int = 86400    # 24 часа
```

### 3. Сервис кэширования

```python
# services/cache.py
import json
import pickle
from typing import Any, Optional, Union
from redis import Redis, ConnectionPool
from ..config import settings

class CacheService:
    """Сервис кэширования с Redis"""
    
    def __init__(self):
        self.redis = Redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            password=settings.redis_password,
            max_connections=settings.redis_max_connections,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Ошибка получения из кэша {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Установить значение в кэш"""
        try:
            ttl = ttl or settings.cache_ttl_default
            serialized = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Ошибка установки в кэш {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Удалить ключ из кэша"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Ошибка удаления из кэша {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Ошибка проверки ключа {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистить все ключи по паттерну"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Ошибка очистки паттерна {pattern}: {e}")
            return 0
```

### 4. Кэширование сессий

```python
# middleware/session_cache.py
from starlette.middleware.base import BaseHTTPMiddleware
from ..services.cache import CacheService

class SessionCacheMiddleware(BaseHTTPMiddleware):
    """Middleware для кэширования сессий в Redis"""
    
    def __init__(self, app, cache_service: CacheService):
        super().__init__(app)
        self.cache = cache_service
    
    async def dispatch(self, request, call_next):
        # Проверяем кэш сессии
        session_id = request.cookies.get("session")
        if session_id:
            cached_session = self.cache.get(f"session:{session_id}")
            if cached_session:
                request.state.cached_session = cached_session
        
        response = await call_next(request)
        
        # Кэшируем обновленную сессию
        if hasattr(request.state, 'cached_session'):
            self.cache.set(
                f"session:{session_id}",
                request.state.cached_session,
                ttl=settings.session_max_age
            )
        
        return response
```

### 5. Кэширование данных

```python
# services/products.py
from ..services.cache import CacheService

class ProductService:
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Получить товар с кэшированием"""
        cache_key = f"product:{product_id}"
        
        # Проверяем кэш
        cached_product = self.cache.get(cache_key)
        if cached_product:
            return Product(**cached_product)
        
        # Загружаем из БД
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            # Кэшируем на 1 час
            self.cache.set(cache_key, product.__dict__, ttl=3600)
        
        return product
    
    def get_products_list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Получить список товаров с кэшированием"""
        cache_key = f"products:list:{skip}:{limit}"
        
        # Проверяем кэш
        cached_products = self.cache.get(cache_key)
        if cached_products:
            return [Product(**p) for p in cached_products]
        
        # Загружаем из БД
        products = db.query(Product).offset(skip).limit(limit).all()
        
        # Кэшируем на 5 минут (часто изменяемые данные)
        self.cache.set(cache_key, [p.__dict__ for p in products], ttl=300)
        
        return products
    
    def invalidate_product_cache(self, product_id: int):
        """Инвалидировать кэш товара"""
        self.cache.delete(f"product:{product_id}")
        # Очищаем все списки товаров
        self.cache.clear_pattern("products:list:*")
```

## Паттерны кэширования

### 1. Кэширование запросов

```python
def cache_query_result(func):
    """Декоратор для кэширования результатов запросов"""
    def wrapper(*args, **kwargs):
        # Создаем ключ кэша на основе параметров
        cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
        
        # Проверяем кэш
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # Выполняем функцию
        result = func(*args, **kwargs)
        
        # Кэшируем результат
        cache_service.set(cache_key, result)
        
        return result
    return wrapper

# Использование
@cache_query_result
def get_orders_by_status(status: str, limit: int = 100):
    return db.query(Order).filter(Order.status == status).limit(limit).all()
```

### 2. Кэширование агрегаций

```python
def get_order_statistics():
    """Получить статистику заказов с кэшированием"""
    cache_key = "order_stats"
    
    cached_stats = cache_service.get(cache_key)
    if cached_stats:
        return cached_stats
    
    # Вычисляем статистику
    stats = {
        'total_orders': db.query(func.count(Order.id)).scalar(),
        'pending_orders': db.query(func.count(Order.id)).filter(Order.status == 'pending').scalar(),
        'completed_orders': db.query(func.count(Order.id)).filter(Order.status == 'completed').scalar(),
        'total_revenue': db.query(func.sum(Order.total_amount)).scalar() or 0
    }
    
    # Кэшируем на 10 минут
    cache_service.set(cache_key, stats, ttl=600)
    
    return stats
```

### 3. Кэширование пользовательских данных

```python
def get_user_profile(user_id: str):
    """Получить профиль пользователя с кэшированием"""
    cache_key = f"user_profile:{user_id}"
    
    cached_profile = cache_service.get(cache_key)
    if cached_profile:
        return cached_profile
    
    # Загружаем из БД
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        profile = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        # Кэшируем на 30 минут
        cache_service.set(cache_key, profile, ttl=1800)
        
        return profile
    
    return None
```

## Мониторинг и метрики

### 1. Redis метрики

```python
def get_redis_metrics():
    """Получить метрики Redis"""
    info = cache_service.redis.info()
    
    return {
        'connected_clients': info['connected_clients'],
        'used_memory_human': info['used_memory_human'],
        'used_memory_peak_human': info['used_memory_peak_human'],
        'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_misses', 1), 1),
        'total_commands_processed': info['total_commands_processed'],
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0)
    }
```

### 2. Кэш-метрики

```python
class CacheMetrics:
    def __init__(self):
        self.hits = 0
        self.misses = 0
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
```

## Развертывание

### 1. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

volumes:
  redis_data:
```

### 2. Production настройки

```python
# production.py
REDIS_CONFIG = {
    'host': 'redis-cluster.example.com',
    'port': 6379,
    'password': 'secure_password',
    'ssl': True,
    'ssl_cert_reqs': 'required',
    'max_connections': 50,
    'retry_on_timeout': True,
    'health_check_interval': 30
}
```

## Заключение

Интеграция Redis значительно улучшит производительность системы за счет:
- Ускорения доступа к часто запрашиваемым данным
- Снижения нагрузки на базу данных
- Улучшения масштабируемости
- Оптимизации использования памяти

Правильная настройка TTL и стратегий инвалидации обеспечит актуальность данных и эффективность кэширования.
