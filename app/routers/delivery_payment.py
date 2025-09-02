"""
Роутер для страницы оплаты доставки
Обрабатывает запросы к странице заглушки оплаты доставки
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.orders import OrderService
from app.constants.delivery import DeliveryOption

router = APIRouter(tags=["delivery"])

# Templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/delivery/payment", response_class=HTMLResponse)
async def delivery_payment_page(
    request: Request,
    order_code: str = None,
    db: Session = Depends(get_db)
):
    """
    Страница оплаты доставки (заглушка)
    
    Args:
        request: HTTP запрос
        order_code: Код заказа (опционально)
        db: Сессия базы данных
    
    Returns:
        HTML страница с информацией о доставке и WhatsApp кнопками
    """
    
    # Формируем базовый текст для WhatsApp
    whatsapp_message = "Здравствуйте! У меня есть вопрос по доставке."
    
    # Если передан код заказа, добавляем информацию о заказе
    if order_code:
        try:
            # Получаем информацию о заказе
            order = OrderService.get_order_by_code(db, order_code)
            if order:
                whatsapp_message = f"""Здравствуйте! У меня есть вопрос по заказу {order_code}.

Товар: {order.product_name}
Количество: {order.qty}
Стоимость: {order.unit_price_rub} ₽

Нужна помощь с доставкой."""
        except Exception:
            # Если не удалось получить заказ, используем базовый текст
            pass
    
    # Добавляем информацию о клиенте, если есть
    if hasattr(request, 'session') and 'customer_name' in request.session:
        customer_name = request.session.get('customer_name')
        if customer_name:
            whatsapp_message += f"\n\nМеня зовут: {customer_name}"
    
    # Добавляем информацию о телефоне, если есть
    if hasattr(request, 'session') and 'customer_phone' in request.session:
        customer_phone = request.session.get('customer_phone')
        if customer_phone:
            whatsapp_message += f"\nМой телефон: {customer_phone}"
    
    # Добавляем стандартную информацию
    whatsapp_message += """

Спасибо!"""
    
    return templates.TemplateResponse("shop/delivery_payment.html", {
        "request": request,
        "whatsapp_message": whatsapp_message
    })


@router.get("/delivery/payment/{order_code}", response_class=HTMLResponse)
async def delivery_payment_with_order(
    request: Request,
    order_code: str,
    db: Session = Depends(get_db)
):
    """
    Страница оплаты доставки для конкретного заказа
    
    Args:
        request: HTTP запрос
        order_code: Код заказа
        db: Сессия базы данных
    
    Returns:
        HTML страница с информацией о заказе и доставке
    """
    
    try:
        # Получаем информацию о заказе
        order = OrderService.get_order_by_code(db, order_code)
        if not order:
            # Если заказ не найден, перенаправляем на общую страницу
            return templates.TemplateResponse("shop/delivery_payment.html", {
                "request": request,
                "whatsapp_message": "Здравствуйте! У меня есть вопрос по доставке.",
                "error": "Заказ не найден"
            })
        
        # Формируем детальный текст для WhatsApp
        whatsapp_message = f"""Здравствуйте! У меня есть вопрос по заказу {order_code}.

Товар: {order.product_name}
Количество: {order.qty}
Стоимость: {order.unit_price_rub} ₽
Статус: {order.status}

Нужна помощь с доставкой."""
        
        # Добавляем информацию о клиенте
        if order.customer_name:
            whatsapp_message += f"\n\nМеня зовут: {order.customer_name}"
        
        if order.phone:
            whatsapp_message += f"\nМой телефон: {order.phone}"
        
        # Добавляем информацию о доставке, если есть
        if order.delivery_option:
            from app.constants.delivery import get_delivery_display_name
            delivery_name = get_delivery_display_name(order.delivery_option)
            whatsapp_message += f"\n\nВыбранная доставка: {delivery_name}"
            
            if order.delivery_cost_rub:
                whatsapp_message += f"\nСтоимость доставки: {order.delivery_cost_rub} ₽"
        
        whatsapp_message += "\n\nСпасибо!"
        
        return templates.TemplateResponse("shop/delivery_payment.html", {
            "request": request,
            "whatsapp_message": whatsapp_message,
            "order": order
        })
        
    except Exception as e:
        # В случае ошибки возвращаем базовый текст
        return templates.TemplateResponse("shop/delivery_payment.html", {
            "request": request,
            "whatsapp_message": "Здравствуйте! У меня есть вопрос по доставке.",
            "error": f"Ошибка при получении заказа: {str(e)}"
        })

