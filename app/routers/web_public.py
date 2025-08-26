from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.auth import authenticate_user, create_user
from ..models import UserRole

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка входа"""
    user = authenticate_user(db, username, password)
    if not user:
        return RedirectResponse(
            url="/login?error=Неверное имя пользователя или пароль",
            status_code=status.HTTP_302_FOUND
        )
    
    # Установка сессии
    request.session["user_id"] = user.username
    return RedirectResponse(url="/?success=Успешный вход", status_code=status.HTTP_302_FOUND)


@router.get("/register")
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка регистрации"""
    if password != confirm_password:
        return RedirectResponse(
            url="/register?error=Пароли не совпадают",
            status_code=status.HTTP_302_FOUND
        )
    
    try:
        user = create_user(db, username, password, UserRole.USER)
        return RedirectResponse(
            url="/login?success=Регистрация успешна. Теперь войдите в систему",
            status_code=status.HTTP_302_FOUND
        )
    except HTTPException as e:
        return RedirectResponse(
            url=f"/register?error={e.detail}",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/logout")
async def logout(request: Request):
    """Выход из системы"""
    request.session.clear()
    return RedirectResponse(url="/?success=Вы вышли из системы", status_code=status.HTTP_302_FOUND)
