from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.auth import authenticate_user, create_user, get_current_user_optional
from ..models import UserRole

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Страница входа"""
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse("login.html", {"request": request, "current_user": current_user})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка входа"""
    print(f"🔐 Попытка входа: {username}")  # Отладочная информация
    
    user = authenticate_user(db, username, password)
    if not user:
        print(f"❌ Аутентификация не удалась для {username}")
        return RedirectResponse(
            url="/login?error=Неверное имя пользователя или пароль",
            status_code=status.HTTP_302_FOUND
        )
    
    # Установка сессии
    request.session["user_id"] = user.username
    print(f"✅ Сессия установлена для {user.username}: {request.session.get('user_id')}")
    
    return RedirectResponse(url="/?success=Успешный вход", status_code=status.HTTP_302_FOUND)


@router.get("/register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Страница регистрации"""
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse("register.html", {"request": request, "current_user": current_user})


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


@router.get("/debug-session")
async def debug_session(request: Request, db: Session = Depends(get_db)):
    """Отладочная информация о сессии"""
    current_user = get_current_user_optional(request, db)
    
    debug_info = {
        "session_data": dict(request.session),
        "user_id_in_session": request.session.get("user_id"),
        "current_user": current_user.username if current_user else None,
        "user_role": current_user.role if current_user else None,
        "headers": dict(request.headers),
        "cookies": dict(request.cookies)
    }
    
    return {"debug_info": debug_info}
