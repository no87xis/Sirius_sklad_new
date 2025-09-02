from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import get_db
from app.services.delivery_notifications import DeliveryNotificationService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/delivery-notifications")
async def delivery_notifications_page(request: Request, db: Session = Depends(get_db)):
    """Страница уведомлений о доставке"""
    upcoming_deliveries = DeliveryNotificationService.get_upcoming_deliveries(db, days_ahead=5)
    overdue_deliveries = DeliveryNotificationService.get_overdue_deliveries(db)
    
    return templates.TemplateResponse("admin/delivery_notifications.html", {
        "request": request,
        "upcoming_deliveries": upcoming_deliveries,
        "overdue_deliveries": overdue_deliveries
    })


@router.post("/admin/delivery-notifications/mark-arrived")
async def mark_batch_arrived(
    batch_id: int = Form(...),
    final_price: float = Form(None),
    db: Session = Depends(get_db)
):
    """Отмечает партию как прибывшую"""
    success = DeliveryNotificationService.mark_batch_as_arrived(db, batch_id, final_price)
    
    if success:
        return {"success": True, "message": "Партия отмечена как прибывшая"}
    else:
        return {"success": False, "message": "Партия не найдена"}


@router.post("/admin/delivery-notifications/update-date")
async def update_delivery_date(
    batch_id: int = Form(...),
    new_date: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обновляет дату доставки"""
    try:
        new_datetime = datetime.fromisoformat(new_date)
        success = DeliveryNotificationService.update_delivery_date(db, batch_id, new_datetime)
        
        if success:
            return {"success": True, "message": "Дата доставки обновлена"}
        else:
            return {"success": False, "message": "Партия не найдена"}
    except ValueError:
        return {"success": False, "message": "Неверный формат даты"}


@router.get("/api/admin/delivery-notifications")
async def get_delivery_notifications_api(db: Session = Depends(get_db)):
    """API для получения уведомлений о доставке"""
    upcoming_deliveries = DeliveryNotificationService.get_upcoming_deliveries(db, days_ahead=5)
    overdue_deliveries = DeliveryNotificationService.get_overdue_deliveries(db)
    
    return {
        "upcoming_deliveries": upcoming_deliveries,
        "overdue_deliveries": overdue_deliveries,
        "total_notifications": len(upcoming_deliveries) + len(overdue_deliveries)
    }
