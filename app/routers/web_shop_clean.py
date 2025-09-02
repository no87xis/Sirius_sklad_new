import uuid
from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.shop_cart import ShopCartService
from ..services.shop_orders import ShopOrderService
from ..services.qr_service import QRService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_session_id(request: Request) -> str:
    """Получает или создаёт ID сессии для корзины"""
    session_id = request.session.get("cart_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["cart_session_id"] = session_id
    return session_id


@router.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request, db: Session = Depends(get_db)):
    """Главная страница магазина"""
    from ..services.products import get_products
    products = get_products(db)
    return templates.TemplateResponse("shop/index.html", {
        "request": request,
        "products": products
    })


@router.get("/shop/cart", response_class=HTMLResponse)
async def cart_page(request: Request, db: Session = Depends(get_db)):
    """Страница корзины"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    return templates.TemplateResponse("shop/cart.html", {
        "request": request,
        "cart": cart_summary
    })


@router.post("/shop/cart/add")
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    """Добавляет товар в корзину"""
    try:
        session_id = get_session_id(request)
        
        from ..schemas.shop_cart import ShopCartCreate
        cart_data = ShopCartCreate(
            session_id=session_id,
            product_id=product_id,
            quantity=quantity
        )
        
        ShopCartService.add_to_cart(db, cart_data)
        return RedirectResponse(url="/shop/cart?success=Товар добавлен в корзину", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/shop/cart?error=add_failed", status_code=303)


@router.post("/shop/cart/remove")
async def remove_from_cart(
    request: Request,
    cart_item_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Удаляет товар из корзины"""
    try:
        ShopCartService.remove_from_cart(db, cart_item_id)
        return RedirectResponse(url="/shop/cart?success=Товар удален из корзины", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/shop/cart?error=remove_failed", status_code=303)


@router.get("/shop/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, db: Session = Depends(get_db)):
    """Страница оформления заказа"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    if not cart_summary.items:
        return RedirectResponse(url="/shop/cart", status_code=303)
    
    from ..services.payments import PaymentService
    payment_methods = PaymentService.get_active_payment_methods(db)
    
    return templates.TemplateResponse("shop/checkout.html", {
        "request": request,
        "cart": cart_summary,
        "payment_methods": payment_methods
    })


@router.post("/checkout")
async def process_checkout(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_city: str = Form(...),
    customer_city_custom: Optional[str] = Form(None),
    payment_method_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Обрабатывает оформление заказа"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    if not cart_summary.items:
        return RedirectResponse(url="/shop/cart", status_code=303)
    
    # Проверяем и обрабатываем город
    final_city = customer_city
    if customer_city == 'custom' and customer_city_custom:
        final_city = customer_city_custom.strip()
    elif customer_city == 'custom' and not customer_city_custom:
        return RedirectResponse(url="/shop/checkout?error=Укажите название города", status_code=303)
    elif not customer_city:
        return RedirectResponse(url="/shop/checkout?error=Выберите город", status_code=303)
    
    try:
        from app.schemas.shop_order import ShopOrderCreate
        
        # Создаем данные заказа
        order_data = ShopOrderCreate(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_city=final_city,
            payment_method_id=payment_method_id,
            cart_items=cart_summary.items
        )
        
        # Создаем заказы
        orders = ShopOrderService.create_orders_from_cart(db, order_data)
        
        if orders:
            # Очищаем корзину
            ShopCartService.clear_cart(db, session_id)
            
            # Формируем коды заказов для редиректа
            order_codes = [order.order_code for order in orders]
            codes_param = ','.join(order_codes)
            
            return RedirectResponse(url=f"/shop/order-success?codes={codes_param}", status_code=303)
        else:
            return RedirectResponse(url="/shop/checkout?error=creation_failed", status_code=303)
            
    except Exception as e:
        return RedirectResponse(url=f"/shop/checkout?error={str(e)}", status_code=303)


@router.get("/shop/order-success", response_class=HTMLResponse)
async def order_success_page(request: Request, codes: str = Query(...), db: Session = Depends(get_db)):
    """Страница успешного создания заказа"""
    order_codes = codes.split(',')
    
    # Получаем информацию о заказах из основной таблицы Order
    orders = []
    for code in order_codes:
        from app.models import Order
        order = db.query(Order).filter(Order.order_code == code).first()
        if order:
            # Генерируем QR-код если его нет
            if not hasattr(order, 'has_qr') or not order.has_qr:
                QRService.generate_qr_for_order(db, order)
            orders.append(order)
    
    return templates.TemplateResponse("shop/order-success.html", {
        "request": request,
        "orders": orders,
        "qr_service": QRService()
    })


@router.get("/shop/order/{order_code}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request, 
    order_code: str, 
    db: Session = Depends(get_db)
):
    """Страница детальной информации о заказе"""
    from app.models import Order
    order = db.query(Order).filter(Order.order_code == order_code).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Генерируем QR-код если его нет
    if not hasattr(order, 'has_qr') or not order.has_qr:
        QRService.generate_qr_for_order(db, order)
    
    return templates.TemplateResponse("shop/order-detail.html", {
        "request": request,
        "order": order,
        "is_public_view": True,
        "qr_service": QRService()
    })


@router.get("/shop/search-order", response_class=HTMLResponse)
async def search_order_page(request: Request):
    """Страница поиска заказа"""
    return templates.TemplateResponse("shop/search-order.html", {"request": request})


def generate_whatsapp_message(orders, request, db=None):
    """Генерирует сообщение для WhatsApp"""
    if not orders:
        return "Здравствуйте! У меня есть вопрос по заказу."
    
    message_parts = ["🛍 Заказ в магазине SIRIUS_GROUPE"]
    message_parts.append("")
    message_parts.append("📋 Детали заказа:")
    
    for i, order in enumerate(orders, 1):
        message_parts.append(f"{i}. {order.product_name or 'Товар'}")
        message_parts.append(f"   Количество: {order.qty}")
        message_parts.append(f"   Стоимость: {order.unit_price_rub * order.qty} ₽")
        message_parts.append(f"   Код заказа: {order.order_code}")
        
        # Добавляем ссылку на QR-страницу если есть
        if order.has_qr:
            qr_url = QRService.get_qr_public_url(order)
            if qr_url:
                message_parts.append(f"   QR-ссылка: {request.base_url}{qr_url}")
        
        message_parts.append(f"   Ссылка: {request.base_url}orders/{order.order_code}")
        message_parts.append("")
    
    total_amount = sum(order.unit_price_rub * order.qty for order in orders)
    message_parts.append(f"💰 Итого: {total_amount} ₽")
    message_parts.append(f"📱 Телефон: {orders[0].phone if orders else ''}")
    message_parts.append(f"👤 Имя: {orders[0].customer_name if orders else ''}")
    
    # Исправляем отображение города
    city = orders[0].client_city if orders and orders[0].client_city else ''
    if city == 'custom':
        city = 'Не указан'
    message_parts.append(f"🏙 Город: {city}")
    message_parts.append("")
    
    # Добавляем информацию о способе оплаты
    from datetime import datetime, timedelta
    
    # Получаем способ оплаты
    payment_method_name = "не указан"
    if orders and orders[0].payment_method_id:
        try:
            from ..services.payments import PaymentService
            payment_method = PaymentService.get_payment_method_by_id(db, orders[0].payment_method_id)
            if payment_method:
                payment_method_name = payment_method.name
        except Exception:
            payment_method_name = "не указан"
    
    message_parts.append(f"💳 Способ оплаты: {payment_method_name}")
    
    # Добавляем информацию о резерве
    message_parts.append("")
    message_parts.append("⚠️ ВАЖНО: Товары резервируются на 48 часов!")
    message_parts.append("В случае отсутствия оплаты резерв снимается.")
    
    return "\n".join(message_parts)
