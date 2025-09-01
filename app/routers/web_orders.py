from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from ..db import get_db
from ..services.auth import get_current_user_optional, get_current_user
from ..services.orders import (
    get_orders, get_order, create_order, update_order, update_order_status,
    delete_order, get_order_statistics, get_orders_by_product, get_orders_by_phone,
    get_last_eur_rate
)
from ..services.products import get_products
from ..services.order_code import OrderCodeService
from ..services.payments import PaymentService
from ..schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate
from ..deps import require_admin_or_manager
from ..models import OrderStatus, PaymentMethodEnum, PaymentMethodModel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user_optional),
    status_filter: Optional[str] = Query(None),
    phone_search: Optional[str] = Query(None),
    code_search: Optional[str] = Query(None)
):
    """Страница списка заказов"""
    # Проверяем авторизацию
    if not current_user:
        return RedirectResponse(url="/login?error=Требуется авторизация для доступа к заказам", status_code=302)
    
    orders = get_orders(db, status_filter=status_filter)
    
    # Фильтрация по телефону
    if phone_search:
        orders = [order for order in orders if phone_search.lower() in order.phone.lower()]
    
    # Фильтрация по коду заказа (только по полному коду)
    if code_search:
        orders = [order for order in orders if order.order_code and code_search.upper() == order.order_code.upper()]
    
    # Получаем статистику
    stats = get_order_statistics(db)
    
    return templates.TemplateResponse(
        "orders/index.html", 
        {
            "request": request, 
            "current_user": current_user, 
            "orders": orders,
            "stats": stats,
            "status_filter": status_filter,
            "phone_search": phone_search,
            "code_search": code_search,
            "statuses": OrderStatus
        }
    )

@router.get("/orders/new", response_class=HTMLResponse)
async def new_order_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Страница создания нового заказа"""
    products = get_products(db)
    last_eur_rate = get_last_eur_rate(db)
    
    # Получаем активные методы оплаты
    payment_methods = PaymentService.get_active_payment_methods(db)
    
    return templates.TemplateResponse(
        "orders/new.html", 
        {
            "request": request, 
            "current_user": current_user, 
            "products": products,
            "last_eur_rate": last_eur_rate,
            "payment_methods": payment_methods,
            "old_payment_methods": PaymentMethodEnum  # Для совместимости
        }
    )

@router.post("/orders", response_class=HTMLResponse)
async def create_order_post(
    request: Request,
    phone: str = Form(...),
    customer_name: Optional[str] = Form(None),
    client_city: Optional[str] = Form(None),
    client_city_custom: Optional[str] = Form(None),
    product_id: int = Form(...),
    qty: int = Form(...),
    unit_price_rub: str = Form(...),
    eur_rate: str = Form(...),
    payment_method: str = Form(...),
    payment_note: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создание нового заказа"""
    try:
        from decimal import Decimal
        
        # Генерируем уникальный код заказа
        order_code = OrderCodeService.generate_unique_order_code(db)
        
        # Обрабатываем город клиента
        final_city = client_city
        if client_city == "custom" and client_city_custom:
            final_city = client_city_custom
        
        order_data = OrderCreate(
            phone=phone,
            customer_name=customer_name,
            client_city=final_city,
            product_id=product_id,
            qty=qty,
            unit_price_rub=Decimal(unit_price_rub),
            eur_rate=Decimal(eur_rate),
            payment_method=PaymentMethodEnum(payment_method),
            payment_note=payment_note,
            order_code=order_code,  # Передаем сгенерированный код
            source="manual"  # Указываем источник
        )
        create_order(db, order_data, current_user.username)
        return RedirectResponse(url="/orders?success=Заказ успешно создан", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return RedirectResponse(url=f"/orders/new?error={str(e)}", status_code=status.HTTP_302_FOUND)

@router.get("/orders/search", response_class=HTMLResponse)
async def search_orders_page(
    request: Request,
    phone: Optional[str] = Query(None, description="Номер телефона для поиска"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Поиск заказов по телефону"""
    orders = []
    if phone:
        orders = get_orders_by_phone(db, phone)
    
    return templates.TemplateResponse(
        "orders/search.html", 
        {"request": request, "current_user": current_user, "orders": orders, "phone": phone}
    )



@router.get("/orders/{order_id:int}/edit", response_class=HTMLResponse)
async def edit_order_page(
    request: Request, 
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница редактирования заказа"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    products = get_products(db)
    return templates.TemplateResponse(
        "orders/edit.html", 
        {
            "request": request, 
            "current_user": current_user, 
            "order": order, 
            "products": products,
            "payment_methods": PaymentMethodEnum
        }
    )

@router.post("/orders/{order_id:int}", response_class=HTMLResponse)
async def update_order_post(
    request: Request,
    order_id: int,
    phone: Optional[str] = Form(None),
    customer_name: Optional[str] = Form(None),
    client_city: Optional[str] = Form(None),
    product_id: Optional[int] = Form(None),
    qty: Optional[int] = Form(None),
    unit_price_rub: Optional[float] = Form(None),
    eur_rate: Optional[float] = Form(None),
    payment_method: Optional[str] = Form(None),
    payment_note: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Обновление заказа"""
    try:
        from decimal import Decimal
        order_data = OrderUpdate(
            phone=phone,
            customer_name=customer_name,
            client_city=client_city,
            product_id=product_id,
            qty=qty,
            unit_price_rub=Decimal(str(unit_price_rub)) if unit_price_rub else None,
            eur_rate=Decimal(str(eur_rate)) if eur_rate else None,
            payment_method=PaymentMethodEnum(payment_method) if payment_method else None,
            payment_note=payment_note
        )
        update_order(db, order_id, order_data)
        return RedirectResponse(url=f"/orders/{order_id}?success=Заказ успешно обновлен", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return RedirectResponse(url=f"/orders/{order_id}/edit?error={str(e)}", status_code=status.HTTP_302_FOUND)

@router.post("/orders/{order_id:int}/status", response_class=HTMLResponse)
async def update_order_status_post(
    request: Request,
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Обновление статуса заказа"""
    try:
        status_data = OrderStatusUpdate(status=status)
        update_order_status(db, order_id, status_data)
        return RedirectResponse(url=f"/orders/{order_id}?success=Статус заказа обновлен", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/orders/{order_id}?error={str(e)}", status_code=302)

@router.post("/orders/{order_id:int}/delete", response_class=HTMLResponse)
async def delete_order_post(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Удаление заказа"""
    try:
        delete_order(db, order_id)
        return RedirectResponse(url="/orders?success=Заказ успешно удален", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return RedirectResponse(url=f"/orders/{order_id}?error={str(e)}", status_code=status.HTTP_302_FOUND)


# Параметрические маршруты (после всех статических)
@router.get("/orders/{order_id:int}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request, 
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Страница детальной информации о заказе"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return templates.TemplateResponse(
        "orders/detail.html", 
        {"request": request, "current_user": current_user, "order": order}
    )


# Параметрические маршруты (после всех статических)




