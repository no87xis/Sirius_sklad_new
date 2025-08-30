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
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/shop", tags=["shop"])


def get_session_id(request: Request) -> str:
    """Получает или создаёт ID сессии для корзины"""
    session_id = request.session.get("cart_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["cart_session_id"] = session_id
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
    
    from app.schemas.shop_cart import ShopCartCreate
    cart_data = ShopCartCreate(
        product_id=product_id,
        quantity=quantity,
        session_id=session_id
    )
    
    try:
        ShopCartService.add_to_cart(db, cart_data)
        return RedirectResponse(url="/shop/cart", status_code=303)
    except Exception as e:
        # В случае ошибки возвращаемся на страницу товара
        return RedirectResponse(url=f"/shop/product/{product_id}?error={str(e)}", status_code=303)


@router.post("/cart/update")
async def update_cart_post(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    """Обновляет корзину (POST)"""
    session_id = get_session_id(request)
    
    if quantity <= 0:
        ShopCartService.remove_from_cart(db, session_id, product_id)
    else:
        ShopCartService.update_cart_item(db, session_id, product_id, quantity)
    
    return RedirectResponse(url="/shop/cart", status_code=303)


@router.post("/cart/clear")
async def clear_cart_post(
    request: Request,
    db: Session = Depends(get_db)
):
    """Очищает корзину (POST)"""
    session_id = get_session_id(request)
    ShopCartService.clear_cart(db, session_id)
    return RedirectResponse(url="/shop/cart", status_code=303)


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
    payment_methods = PaymentService.get_active_payment_methods(db)
    
    return templates.TemplateResponse("shop/checkout.html", {
        "request": request,
        "cart": cart_summary,
        "payment_methods": payment_methods
    })


@router.post("/checkout")
async def create_order_post(
    request: Request,
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_city: Optional[str] = Form(None),
    payment_method_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Создаёт заказы из корзины (POST)"""
    session_id = get_session_id(request)
    
    # Проверяем валидность корзины
    errors = ShopCartService.validate_cart(db, session_id)
    if errors:
        # Возвращаемся на страницу оформления с ошибками
        return RedirectResponse(
            url=f"/shop/checkout?errors={'&'.join(errors)}", 
            status_code=303
        )
    
    # Получаем товары из корзины
    cart_items = ShopCartService.get_cart_items(db, session_id)
    
    # Создаём данные для заказа
    from app.schemas.shop_order import ShopOrderCreate
    order_data = ShopOrderCreate(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_city=customer_city,
        payment_method_id=payment_method_id,
        cart_items=[{"product_id": item.product_id, "quantity": item.quantity} for item in cart_items]
    )
    
    try:
        orders = ShopOrderService.create_orders_from_cart(db, order_data)
        
        # Очищаем корзину
        ShopCartService.clear_cart(db, session_id)
        
        # Перенаправляем на страницу успешного заказа
        order_codes = [order.order_code for order in orders]
        return RedirectResponse(
            url=f"/shop/order-success?codes={','.join(order_codes)}", 
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/shop/checkout?error={str(e)}", 
            status_code=303
        )


def generate_whatsapp_message(orders):
    """Генерирует сообщение для WhatsApp"""
    if not orders:
        return "Здравствуйте! У меня есть вопрос по заказу."
    
    message_parts = ["Здравствуйте! Я оформил заказ:"]
    
    for order in orders:
        message_parts.append(f"• {order.product_name} - {order.quantity} шт. - {order.total_amount} ₽")
    
    total_amount = sum(order.total_amount for order in orders)
    message_parts.append(f"Общая сумма: {total_amount} ₽")
    
    # Добавляем ссылки на заказы
    message_parts.append("Ссылки на заказы:")
    for order in orders:
        message_parts.append(f"• {order.order_code}: https://sirius-shop.ru/shop/order/{order.order_code}?phone={order.customer_phone}")
    
    return "\n".join(message_parts)


@router.get("/order-success", response_class=HTMLResponse)
async def order_success(
    request: Request,
    codes: str,
    db: Session = Depends(get_db)
):
    """Страница успешного создания заказа"""
    order_codes = codes.split(',')
    
    # Получаем информацию о заказах
    orders = []
    for code in order_codes:
        # Ищем заказ по коду (без телефона для отображения)
        from app.models import ShopOrder
        order = db.query(ShopOrder).filter(ShopOrder.order_code == code).first()
        if order:
            orders.append(order)
    
    return templates.TemplateResponse("shop/order-success.html", {
        "request": request,
        "orders": orders,
        "generate_whatsapp_message": generate_whatsapp_message
    })


@router.get("/order/{order_code}", response_class=HTMLResponse)
async def view_order(
    request: Request,
    order_code: str,
    phone: str,
    db: Session = Depends(get_db)
):
    """Просмотр заказа по коду и телефону"""
    order = ShopOrderService.get_order_by_code_and_phone(db, order_code, phone)
    
    if not order:
        return templates.TemplateResponse("shop/order-not-found.html", {
            "request": request,
            "order_code": order_code
        })
    
    return templates.TemplateResponse("shop/order-detail.html", {
        "request": request,
        "order": order
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


# Админка заказов магазина
@router.get("/admin/orders", response_class=HTMLResponse)
async def shop_admin_orders(
    request: Request,
    status_filter: Optional[str] = Query(None),
    phone_search: Optional[str] = Query(None),
    code_search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Страница управления заказами магазина (админка)"""
    # Получаем все заказы
    orders = ShopOrderService.get_recent_orders(db, limit=1000)
    
    # Фильтрация по статусу
    if status_filter:
        orders = [order for order in orders if order.status == status_filter]
    
    # Фильтрация по телефону
    if phone_search:
        orders = [order for order in orders if phone_search.lower() in order.customer_phone.lower()]
    
    # Фильтрация по коду заказа
    if code_search:
        orders = [order for order in orders if code_search.upper() == order.order_code.upper()]
    
    # Получаем аналитику
    analytics = ShopOrderService.get_analytics(db)
    
    return templates.TemplateResponse("shop/admin/orders.html", {
        "request": request,
        "orders": orders,
        "analytics": analytics,
        "status_filter": status_filter,
        "phone_search": phone_search,
        "code_search": code_search
    })


@router.get("/admin/orders/{order_id:int}", response_class=HTMLResponse)
async def shop_admin_order_detail(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    """Страница детального просмотра заказа магазина (админка)"""
    from app.models import ShopOrder
    order = db.query(ShopOrder).filter(ShopOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return templates.TemplateResponse("shop/admin/order-detail.html", {
        "request": request,
        "order": order
    })


@router.post("/admin/orders/{order_id:int}/reserve")
async def shop_admin_reserve_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Резервирует товар для заказа (API)"""
    try:
        success = ShopOrderService.reserve_product_on_payment(db, order_id)
        if success:
            return {"success": True, "message": "Товар успешно зарезервирован"}
        else:
            return {"success": False, "message": "Не удалось зарезервировать товар"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка: {str(e)}"}
