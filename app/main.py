from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .db import engine, Base, get_db
from .routers import web_public, web_admin, web_products, api
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
    max_age=settings.session_max_age
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(web_public.router)
app.include_router(web_admin.router, prefix="/admin")
app.include_router(web_products.router)
app.include_router(api.router, prefix="/api")


@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """Главная страница"""
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
