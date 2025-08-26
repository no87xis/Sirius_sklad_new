from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.sessions import SessionMiddleware
from .config import settings
from .db import engine, Base
from .routers import web_public, web_admin, api

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
app.include_router(api.router, prefix="/api")


@app.get("/")
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
