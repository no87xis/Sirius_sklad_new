from fastapi import APIRouter, Request, Depends, Query, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.admin import (
    get_users, get_user, get_user_by_username, create_user, update_user, delete_user,
    get_user_statistics, get_operation_logs, get_log_statistics,
    create_operation_log
)
from ..schemas.user import UserCreate, UserUpdate
from ..deps import require_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Главная страница админ-панели"""
    user_stats = get_user_statistics(db)
    log_stats = get_log_statistics(db)
    
    # Получаем уведомления о доставке
    from ..services.delivery_notifications import DeliveryNotificationService
    upcoming_deliveries = DeliveryNotificationService.get_upcoming_deliveries(db, days_ahead=5)
    overdue_deliveries = DeliveryNotificationService.get_overdue_deliveries(db)
    
    delivery_notifications = {
        "upcoming_deliveries": upcoming_deliveries,
        "overdue_deliveries": overdue_deliveries,
        "total_notifications": len(upcoming_deliveries) + len(overdue_deliveries)
    }
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request, 
            "current_user": current_user,
            "user_stats": user_stats,
            "log_stats": log_stats,
            "delivery_notifications": delivery_notifications
        }
    )

@router.get("/admin/metrics", response_class=HTMLResponse)
async def admin_metrics(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница метрик производительности"""
    return templates.TemplateResponse(
        "admin/metrics.html",
        {"request": request, "current_user": current_user}
    )

@router.get("/admin/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница управления пользователями"""
    users = get_users(db)
    stats = get_user_statistics(db)
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request, 
            "current_user": current_user,
            "users": users,
            "stats": stats
        }
    )

@router.get("/admin/users/new", response_class=HTMLResponse)
async def new_user_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница создания нового пользователя"""
    return templates.TemplateResponse(
        "admin/users/new.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/admin/users", response_class=HTMLResponse)
async def create_user_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Создание нового пользователя"""
    try:
        user_data = UserCreate(
            username=username,
            password=password,
            role=role
        )
        new_user = create_user(db, user_data)
        
        # Логируем операцию
        create_operation_log(
            db, current_user.username, "user_create",
            f"Создан пользователь {username} с ролью {role}"
        )
        
        return RedirectResponse(
            url="/admin/users?success=Пользователь успешно создан", 
            status_code=302
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/users/new?error={str(e)}", 
            status_code=302
        )

@router.get("/admin/users/{username}", response_class=HTMLResponse)
async def user_detail_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница детальной информации о пользователе"""
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return templates.TemplateResponse(
        "admin/users/detail.html",
        {"request": request, "current_user": current_user, "user": user}
    )

@router.get("/admin/users/{username}/edit", response_class=HTMLResponse)
async def edit_user_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница редактирования пользователя"""
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return templates.TemplateResponse(
        "admin/users/edit.html",
        {"request": request, "current_user": current_user, "user": user}
    )

@router.post("/admin/users/{username}", response_class=HTMLResponse)
async def update_user_post(
    request: Request,
    username: str,
    new_username: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Обновление пользователя"""
    try:
        user_data = UserUpdate(
            username=new_username,
            role=role,
            password=password
        )
        updated_user = update_user(db, username, user_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Логируем операцию
        create_operation_log(
            db, current_user.username, "user_update",
            f"Обновлен пользователь {updated_user.username}"
        )
        
        return RedirectResponse(
            url=f"/admin/users/{username}?success=Пользователь успешно обновлен", 
            status_code=302
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/users/{username}/edit?error={str(e)}", 
            status_code=302
        )

@router.post("/admin/users/{username}/delete", response_class=HTMLResponse)
async def delete_user_post(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Удаление пользователя"""
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Нельзя удалить самого себя
        if user.username == current_user.username:
            return RedirectResponse(
                url="/admin/users?error=Нельзя удалить самого себя", 
                status_code=302
            )
        
        old_username = user.username
        delete_user(db, username)
        
        # Логируем операцию
        create_operation_log(
            db, current_user.username, "user_delete",
            f"Удален пользователь {old_username}"
        )
        
        return RedirectResponse(
            url="/admin/users?success=Пользователь успешно удален", 
            status_code=302
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/users?error={str(e)}", 
            status_code=302
        )

@router.get("/admin/logs", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    user_id: Optional[str] = Query(None),
    operation_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin())
):
    """Страница просмотра логов операций"""
    # Парсим даты
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    
    if end_date:
        try:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass
    
    logs = get_operation_logs(
        db, 
        user_id=user_id,
        operation_type=operation_type,
        start_date=parsed_start_date,
        end_date=parsed_end_date
    )
    
    stats = get_log_statistics(db)
    
    return templates.TemplateResponse(
        "admin/logs.html",
        {
            "request": request, 
            "current_user": current_user,
            "logs": logs,
            "stats": stats,
            "filters": {
                "user_id": user_id,
                "operation_type": operation_type,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    )
