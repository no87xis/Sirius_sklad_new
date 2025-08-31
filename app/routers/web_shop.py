from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.db import get_db
from app.services.products import get_products
from app.services.shop_cart import ShopCartService
from app.services.shop_orders import ShopOrderService
from app.services.payments import PaymentService
from app.services.qr_service import QRService
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/shop", tags=["shop"])


def get_session_id(request: Request) -> str:
    """Получает или создаёт ID сессии для корзины"""
    session_id = request.session.get("cart_session_id")
    print(f"DEBUG: get_session_id called, existing session_id: {session_id}")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["cart_session_id"] = session_id
        print(f"DEBUG: Created new session_id: {session_id}")
    else:
        print(f"DEBUG: Using existing session_id: {session_id}")
    return session_id


@router.get("/", response_class=HTMLResponse)
async def shop_catalog(
    request: Request,
    db: Session = Depends(get_db)
):
    """Каталог товаров магазина"""
    products = get_products(db)
    
    # Debug: проверяем фотографии
    for product in products:
        print(f"DEBUG: Товар {product.id} '{product.name}' - фото: {len(product.photos)}, главное: {product.main_photo is not None}")
    
    # Получаем количество товаров в корзине
    session_id = get_session_id(request)
    cart_count = ShopCartService.get_cart_count(db, session_id)
    
    return templates.TemplateResponse("shop/catalog.html", {
        "request": request,
        "products": products,
        "cart_count": cart_count
    })


@router.get("/product/{product_id:int}", response_class=HTMLResponse)
async def shop_product_detail(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db)
):
    """Страница товара в магазине"""
    from app.services.products import get_product
    
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Получаем количество товаров в корзине
    session_id = get_session_id(request)
    cart_count = ShopCartService.get_cart_count(db, session_id)
    
    return templates.TemplateResponse("shop/product.html", {
        "request": request,
        "product": product,
        "cart_count": cart_count
    })


@router.get("/cart", response_class=HTMLResponse)
async def shop_cart(
    request: Request,
    db: Session = Depends(get_db)
):
    """Корзина магазина"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    return templates.TemplateResponse("shop/cart.html", {
        "request": request,
        "cart": cart_summary
    })


@router.post("/cart/add")
async def add_to_cart_post(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    """Добавляет товар в корзину (POST)"""
    session_id = get_session_id(request)
    
    try:
        from app.schemas.shop_cart import ShopCartCreate
        cart_data = ShopCartCreate(session_id=session_id, product_id=product_id, quantity=quantity)
        result = ShopCartService.add_to_cart(db, cart_data)
        if result:
            return RedirectResponse(url="/shop/cart", status_code=303)
        else:
            return RedirectResponse(url="/shop/cart?error=add_failed", status_code=303)
    except Exception as e:
        print(f"ERROR adding to cart: {str(e)}")
        return RedirectResponse(url=f"/shop/cart?error={str(e)}", status_code=303)


@router.post("/cart/remove")
async def remove_from_cart_post(
    request: Request,
    product_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Удаляет товар из корзины (POST)"""
    session_id = get_session_id(request)
    
    try:
        success = ShopCartService.remove_from_cart(db, session_id, product_id)
        return RedirectResponse(url="/shop/cart", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/shop/cart?error={str(e)}", status_code=303)


@router.get("/checkout", response_class=HTMLResponse)
async def shop_checkout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Страница оформления заказа"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    if not cart_summary.items:
        return RedirectResponse(url="/shop/cart", status_code=303)
    
    # Получаем способы оплаты
    from app.models import PaymentMethod
    payment_methods = db.query(PaymentMethod).all()
    
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
    payment_method_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Обрабатывает оформление заказа"""
    session_id = get_session_id(request)
    cart_summary = ShopCartService.get_cart_summary(db, session_id)
    
    if not cart_summary.items:
        return RedirectResponse(url="/shop/cart", status_code=303)
    
    try:
        from app.schemas.shop_order import ShopOrderCreate
        
        # Создаем данные заказа
        order_data = ShopOrderCreate(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_city=customer_city,
            payment_method_id=payment_method_id,
            cart_items=cart_summary.items
        )
        
        # Создаем заказы
        orders = ShopOrderService.create_orders_from_cart(db, order_data)
        
        if orders:
            print(f"DEBUG: Orders created successfully: {len(orders)}")
            for order in orders:
                print(f"DEBUG: Order {order.id}: code={order.order_code}, product={order.product_name}")
            
            # Очищаем корзину
            ShopCartService.clear_cart(db, session_id)
            
            # Формируем коды заказов для редиректа
            order_codes = [order.order_code for order in orders]
            codes_param = ','.join(order_codes)
            print(f"DEBUG: Redirecting to order-success with codes: {codes_param}")
            
            return RedirectResponse(url=f"/shop/order-success?codes={codes_param}", status_code=303)
        else:
            return RedirectResponse(url="/shop/checkout?error=creation_failed", status_code=303)
            
    except Exception as e:
        return RedirectResponse(url=f"/shop/checkout?error={str(e)}", status_code=303)


def generate_whatsapp_message(orders, request, db=None):
    """Генерирует сообщение для WhatsApp"""
    if not orders:
        return "Здравствуйте! У меня есть вопрос по заказу."
    
    message_parts = ["🛍 Заказ в магазине SIRIUS_GROUPE"]
    message_parts.append("")
    message_parts.append("📋 Детали заказа:")
    
    for i, order in enumerate(orders, 1):
        message_parts.append(f"{i}. {order.product_name or 'Товар'}")
        message_parts.append(f"   Количество: {order.quantity}")
        message_parts.append(f"   Стоимость: {order.total_amount} ₽")
        message_parts.append(f"   Код заказа: {order.order_code}")
        
        # Добавляем ссылку на QR-страницу если есть
        if order.has_qr:
            qr_url = QRService.get_qr_public_url(order)
            if qr_url:
                message_parts.append(f"   QR-ссылка: {request.base_url}{qr_url}")
        
        message_parts.append(f"   Ссылка: {request.base_url}shop/order/{order.order_code}")
        message_parts.append("")
    
    total_amount = sum(order.total_amount for order in orders)
    message_parts.append(f"💰 Итого: {total_amount} ₽")
    message_parts.append(f"📱 Телефон: {orders[0].customer_phone if orders else ''}")
    message_parts.append(f"👤 Имя: {orders[0].customer_name if orders else ''}")
    
    # Исправляем отображение города
    city = orders[0].customer_city if orders and orders[0].customer_city else ''
    if city == 'custom':
        city = 'Не указан'
    message_parts.append(f"🏙 Город: {city}")
    message_parts.append("")
    
    # Добавляем информацию о способе оплаты
    from datetime import datetime, timedelta
    
    # Получаем способ оплаты
    payment_method_name = "не указан"
    if orders and orders[0].payment_method_id:
        # Сначала пробуем получить из relationship
        if hasattr(orders[0], 'payment_method') and orders[0].payment_method:
            payment_method_name = orders[0].payment_method.name
        # Если не получилось, берем из поля payment_method_name
        elif hasattr(orders[0], 'payment_method_name') and orders[0].payment_method_name:
            payment_method_name = orders[0].payment_method_name
        # Если и это не работает, делаем запрос к базе
        elif db:
            try:
                from app.models import PaymentMethod
                payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == orders[0].payment_method_id).first()
                if payment_method:
                    payment_method_name = payment_method.name
            except Exception as e:
                print(f"ERROR getting payment method from DB: {str(e)}")
                payment_method_name = "не указан"
    
    if orders and hasattr(orders[0], 'created_at') and orders[0].created_at:
        created_at = orders[0].created_at
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        reserve_until = created_at + timedelta(hours=48)
        message_parts.append(f"⏰ Резерв до {reserve_until.strftime('%H:%M %d.%m.%Y')}")
    else:
        now = datetime.now()
        reserve_until = now + timedelta(hours=48)
        message_parts.append(f"⏰ Резерв до {reserve_until.strftime('%H:%M %d.%m.%Y')}")
    
    message_parts.append(f"💳 Способ оплаты: {payment_method_name}")
    
    return "\n".join(message_parts)


@router.get("/order-success", response_class=HTMLResponse)
async def order_success(
    request: Request,
    codes: str,
    db: Session = Depends(get_db)
):
    """Страница успешного создания заказа"""
    order_codes = codes.split(',')
    print(f"DEBUG: order_success called with codes: {codes}")
    
    # Получаем информацию о заказах
    orders = []
    for code in order_codes:
        # Ищем заказ по коду (без телефона для отображения)
        from app.models import ShopOrder
        order = db.query(ShopOrder).filter(ShopOrder.order_code == code).first()
        print(f"DEBUG: Looking for order with code {code}, found: {order is not None}")
        if order:
            print(f"DEBUG: Order found: {order.order_code}, product: {order.product_name}")
            # Генерируем QR-код если его нет
            if not order.has_qr:
                QRService.generate_qr_for_order(db, order)
            orders.append(order)
    
    print(f"DEBUG: Total orders found: {len(orders)}")
    
    return templates.TemplateResponse("shop/order-success.html", {
        "request": request,
        "orders": orders,
        "generate_whatsapp_message": generate_whatsapp_message,
        "qr_service": QRService
    })


@router.get("/order/{order_code}", response_class=HTMLResponse)
async def view_order(
    request: Request,
    order_code: str,
    db: Session = Depends(get_db)
):
    """Просмотр заказа по коду"""
    from app.models import ShopOrder
    order = db.query(ShopOrder).filter(ShopOrder.order_code == order_code).first()
    
    if not order:
        return templates.TemplateResponse("shop/order-not-found.html", {
            "request": request,
            "order_code": order_code
        })
    
    # Генерируем QR-код если его нет
    if not order.has_qr:
        QRService.generate_qr_for_order(db, order)
    
    return templates.TemplateResponse("shop/order-detail.html", {
        "request": request,
        "order": order,
        "qr_service": QRService
    })


@router.get("/search-order", response_class=HTMLResponse)
async def search_order_page(request: Request):
    """Страница поиска заказа"""
    return templates.TemplateResponse("shop/search-order.html", {
        "request": request
    })


@router.post("/search-order")
async def search_order_post(
    request: Request,
    order_code: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    """Поиск заказа (POST)"""
    from app.schemas.shop_order import ShopOrderSearch
    search_data = ShopOrderSearch(order_code=order_code, phone=phone)
    
    orders = ShopOrderService.search_orders(db, search_data)
    
    if not orders:
        return templates.TemplateResponse("shop/search-order.html", {
            "request": request,
            "error": "Заказы не найдены. Проверьте код заказа и номер телефона."
        })
    
    # Если найден один заказ, перенаправляем на его страницу
    if len(orders) == 1:
        return RedirectResponse(
            url=f"/shop/order/{orders[0].order_code}?phone={phone}", 
            status_code=303
        )
    
    # Если найдено несколько заказов, показываем список
    return templates.TemplateResponse("shop/orders-list.html", {
        "request": request,
        "orders": orders,
        "phone": phone
    })


# Публичный роут для доступа по QR-коду
@router.get("/o/{qr_token}", response_class=HTMLResponse)
async def public_order_view(
    request: Request,
    qr_token: str,
    db: Session = Depends(get_db)
):
    """Публичный просмотр заказа по QR-токену (без авторизации)"""
    # Проверяем валидность токена
    if not QRService.is_valid_qr_token(qr_token):
        raise HTTPException(status_code=404, detail="Неверный QR-код")
    
    # Получаем заказ по QR-токену
    order = QRService.get_order_by_qr_token(db, qr_token)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Проверяем, что заказ не отменен
    from app.models import ShopOrderStatus
    if order.status == ShopOrderStatus.CANCELLED:
        raise HTTPException(status_code=404, detail="Заказ отменен")
    
    return templates.TemplateResponse("shop/order-detail.html", {
        "request": request,
        "order": order,
        "qr_service": QRService,
        "is_public_view": True  # Флаг для отображения публичной версии
    })
