from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .db import engine, Base, get_db
from .services.auth import get_current_user_optional

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Сириус - Система учёта склада",
    description="Веб-приложение для управления складом, заказами и поставками",
    version="1.0.0"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=settings.session_max_age,
    same_site="lax",
    https_only=False
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# ВАЖНО: Импортируем роутеры ПОСЛЕ создания app
# Это предотвращает циклические импорты

# Основные веб-роутеры
from .routers import web_public
app.include_router(web_public.router)

from .routers import web_products
app.include_router(web_products.router)

from .routers import web_orders
app.include_router(web_orders.router)

from .routers import web_shop
app.include_router(web_shop.router)

# API роутеры
from .routers import shop_api
app.include_router(shop_api.router, prefix="/api")

from .routers import shop_admin
app.include_router(shop_admin.router)

# Админ-панель
from .routers import web_admin_panel
app.include_router(web_admin_panel.router)

# Аналитика
from .routers import web_analytics
app.include_router(web_analytics.router)

# QR-сканер
from .routers import qr_scanner
app.include_router(qr_scanner.router)

# Дополнительные API
from .routers import api
app.include_router(api.router)

# Роуты для основных страниц
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """Главная страница"""
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy", 
        "message": "Sirius Group работает!",
        "features": [
            "Полный функционал склада",
            "Магазин с корзиной",
            "Аналитика и отчеты",
            "Админ-панель",
            "QR-коды и сканер",
            "Управление заказами",
            "Управление продуктами"
        ]
    }

@app.get("/features")
async def features_list():
    """Список всех функций сайта"""
    return {
        "features": {
            "warehouse": "Управление складом и остатками",
            "shop": "Интернет-магазин с корзиной",
            "orders": "Система заказов и поставок",
            "analytics": "Аналитика продаж и остатков",
            "admin": "Административная панель",
            "qr": "QR-коды и сканер",
            "reports": "Отчеты и экспорт данных",
            "users": "Управление пользователями"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
