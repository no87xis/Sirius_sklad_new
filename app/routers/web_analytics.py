from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.analytics import (
    get_sales_report, get_inventory_report, get_supply_report, 
    get_profit_analysis, export_sales_to_csv, export_inventory_to_csv,
    get_dashboard_stats
)
from ..services.products import get_products
from ..deps import require_admin_or_manager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Главная страница аналитики"""
    stats = get_dashboard_stats(db)
    
    return templates.TemplateResponse(
        "analytics/dashboard.html",
        {"request": request, "current_user": current_user, "stats": stats}
    )

@router.get("/analytics/sales", response_class=HTMLResponse)
async def sales_report_page(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница отчета по продажам"""
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
            # Добавляем 23:59:59 к конечной дате
            parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass
    
    # Получаем отчет
    report = get_sales_report(db, parsed_start_date, parsed_end_date, product_id)
    
    # Получаем список товаров для фильтра
    products = get_products(db)
    
    return templates.TemplateResponse(
        "analytics/sales_report.html",
        {
            "request": request, 
            "current_user": current_user, 
            "report": report,
            "products": products,
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id
        }
    )

@router.get("/analytics/inventory", response_class=HTMLResponse)
async def inventory_report_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница отчета по остаткам"""
    report = get_inventory_report(db)
    
    return templates.TemplateResponse(
        "analytics/inventory_report.html",
        {"request": request, "current_user": current_user, "report": report}
    )

@router.get("/analytics/supplies", response_class=HTMLResponse)
async def supply_report_page(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница отчета по поставкам"""
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
    
    report = get_supply_report(db, parsed_start_date, parsed_end_date)
    
    return templates.TemplateResponse(
        "analytics/supply_report.html",
        {
            "request": request, 
            "current_user": current_user, 
            "report": report,
            "start_date": start_date,
            "end_date": end_date
        }
    )

@router.get("/analytics/profit", response_class=HTMLResponse)
async def profit_analysis_page(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница анализа прибыли"""
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
    
    analysis = get_profit_analysis(db, parsed_start_date, parsed_end_date)
    
    return templates.TemplateResponse(
        "analytics/profit_analysis.html",
        {
            "request": request, 
            "current_user": current_user, 
            "analysis": analysis,
            "start_date": start_date,
            "end_date": end_date
        }
    )

@router.get("/analytics/export/sales", response_class=Response)
async def export_sales_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Экспорт продаж в CSV"""
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
    
    csv_data = export_sales_to_csv(db, parsed_start_date, parsed_end_date)
    
    filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/analytics/export/inventory", response_class=Response)
async def export_inventory_csv(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Экспорт остатков в CSV"""
    csv_data = export_inventory_to_csv(db)
    
    filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
