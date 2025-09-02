from fastapi import APIRouter, Depends, HTTPException, status, Request, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.db import get_db
from app.services.shop_cart import ShopCartService
from app.services.shop_orders import ShopOrderService
from app.schemas.shop_cart import ShopCartCreate, ShopCartUpdate, ShopCartSummary
from app.schemas.shop_order import ShopOrderCreate, ShopOrderResponse, ShopOrderSearch, ShopOrderUpdate

router = APIRouter(prefix="/api/shop", tags=["shop"])


def get_session_id(request: Request) -> str:
    """Получает или создаёт ID сессии для корзины"""
    session_id = request.session.get("cart_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["cart_session_id"] = session_id
    return session_id


# Корзина
@router.post("/cart/add", response_model=dict)
async def add_to_cart(
    cart_data: ShopCartCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Добавляет товар в корзину"""
    session_id = get_session_id(request)
    cart_data.session_id = session_id
    
    try:
        cart_item = ShopCartService.add_to_cart(db, cart_data)
        return {"success": True, "message": "Товар добавлен в корзину", "cart_item_id": cart_item.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cart/add-form", response_model=dict)
async def add_to_cart_form(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    """Добавляет товар в корзину через form data (для JavaScript)"""
    try:
        session_id = get_session_id(request)
        
        # Проверяем, что товар существует
        from app.models.product import Product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"success": False, "message": "Товар не найден"}
        
        # Проверяем доступность товара
        if product.quantity <= 0 and product.availability_status not in ['IN_TRANSIT', 'ON_ORDER']:
            return {"success": False, "message": f"Товар '{product.name}' недоступен (остаток: {product.quantity})"}
        
        from app.schemas.shop_cart import ShopCartCreate
        cart_data = ShopCartCreate(session_id=session_id, product_id=product_id, quantity=quantity)
        cart_item = ShopCartService.add_to_cart(db, cart_data)
        return {"success": True, "message": "Товар добавлен в корзину", "cart_item_id": cart_item.id}
    except Exception as e:
        print(f"Error adding to cart: {e}")  # Логируем ошибку
        return {"success": False, "message": f"Ошибка сервера: {str(e)}"}


@router.put("/cart/update/{product_id}")
async def update_cart_item(
    product_id: int,
    quantity: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновляет количество товара в корзине"""
    session_id = get_session_id(request)
    
    if quantity <= 0:
        # Удаляем товар из корзины
        success = ShopCartService.remove_from_cart(db, session_id, product_id)
        if success:
            return {"success": True, "message": "Товар удалён из корзины"}
        else:
            raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    
    cart_item = ShopCartService.update_cart_item(db, session_id, product_id, quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    
    return {"success": True, "message": "Количество обновлено", "quantity": cart_item.quantity}


@router.delete("/cart/remove/{product_id}")
async def remove_from_cart(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Удаляет товар из корзины"""
    session_id = get_session_id(request)
    success = ShopCartService.remove_from_cart(db, session_id, product_id)
    
    if success:
        return {"success": True, "message": "Товар удалён из корзины"}
    else:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")


@router.get("/cart", response_model=ShopCartSummary)
async def get_cart(request: Request, db: Session = Depends(get_db)):
    """Получает содержимое корзины"""
    session_id = get_session_id(request)
    return ShopCartService.get_cart_summary(db, session_id)


@router.delete("/cart/clear")
async def clear_cart(request: Request, db: Session = Depends(get_db)):
    """Очищает корзину"""
    session_id = get_session_id(request)
    success = ShopCartService.clear_cart(db, session_id)
    
    if success:
        return {"success": True, "message": "Корзина очищена"}
    else:
        return {"success": True, "message": "Корзина уже пуста"}


@router.get("/cart/count")
async def get_cart_count(request: Request, db: Session = Depends(get_db)):
    """Получает количество товаров в корзине"""
    session_id = get_session_id(request)
    count = ShopCartService.get_cart_count(db, session_id)
    return {"count": count}


# Заказы
@router.post("/orders", response_model=List[ShopOrderResponse])
async def create_orders(
    order_data: ShopOrderCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Создаёт заказы из корзины"""
    session_id = get_session_id(request)
    
    # Проверяем валидность корзины
    errors = ShopCartService.validate_cart(db, session_id)
    if errors:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибки в корзине: {'; '.join(errors)}"
        )
    
    try:
        orders = ShopOrderService.create_orders_from_cart(db, order_data)
        
        # Очищаем корзину после создания заказов
        ShopCartService.clear_cart(db, session_id)
        
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/search", response_model=List[ShopOrderResponse])
async def search_orders(
    search_data: ShopOrderSearch,
    db: Session = Depends(get_db)
):
    """Поиск заказов по коду и телефону"""
    orders = ShopOrderService.search_orders(db, search_data)
    
    if not orders:
        raise HTTPException(
            status_code=404, 
            detail="Заказы не найдены. Проверьте код заказа и номер телефона."
        )
    
    return orders


@router.get("/orders/{order_code}", response_model=ShopOrderResponse)
async def get_order_by_code(
    order_code: str,
    phone: str,
    db: Session = Depends(get_db)
):
    """Получает заказ по коду и телефону"""
    order = ShopOrderService.get_order_by_code_and_phone(db, order_code, phone)
    
    if not order:
        raise HTTPException(
            status_code=404, 
            detail="Заказ не найден. Проверьте код заказа и номер телефона."
        )
    
    return order


# Админские эндпоинты (для менеджеров)
@router.put("/admin/orders/{order_id}", response_model=ShopOrderResponse)
async def update_order(
    order_id: int,
    update_data: ShopOrderUpdate,
    db: Session = Depends(get_db)
):
    """Обновляет заказ (для менеджера)"""
    order = ShopOrderService.update_order(db, order_id, update_data)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return order


@router.post("/admin/orders/expire-reserved")
async def expire_reserved_orders(db: Session = Depends(get_db)):
    """Снимает резерв с истёкших заказов (для фонового процесса)"""
    expired_count = ShopOrderService.expire_reserved_orders(db)
    return {"expired_count": expired_count, "message": f"Снят резерв с {expired_count} заказов"}


@router.get("/admin/orders/analytics")
async def get_orders_analytics(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Получает аналитику по заказам"""
    from datetime import datetime
    
    # Парсим даты если переданы
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты начала")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты окончания")
    
    analytics = ShopOrderService.get_analytics(db, start_dt, end_dt)
    return analytics


# API эндпоинты для управления фото товаров
@router.get("/products/{product_id}/photos")
async def get_product_photos(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Получает все фото товара"""
    from app.services.product_photos import ProductPhotoService
    
    photos = ProductPhotoService.get_product_photos(db, product_id)
    return photos


@router.post("/products/{product_id}/photos")
async def upload_product_photo(
    product_id: int,
    photo: UploadFile = File(...),
    is_main: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db)
):
    """Загружает новое фото для товара"""
    from app.services.product_photos import ProductPhotoService
    
    try:
        photo_data = await ProductPhotoService.save_photo(
            photo, 
            product_id, 
            db,
            is_main=is_main, 
            sort_order=sort_order
        )
        return {"success": True, "photo": photo_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/products/photos/{photo_id}")
async def delete_product_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    """Удаляет фото товара"""
    from app.services.product_photos import ProductPhotoService
    
    success = ProductPhotoService.delete_photo(db, photo_id)
    if success:
        return {"success": True, "message": "Фото удалено"}
    else:
        raise HTTPException(status_code=404, detail="Фото не найдено")


@router.patch("/products/photos/{photo_id}")
async def update_product_photo(
    photo_id: int,
    is_main: bool = Form(False),
    sort_order: int = Form(None),
    db: Session = Depends(get_db)
):
    """Обновляет фото товара (главное фото, порядок)"""
    from app.services.product_photos import ProductPhotoService
    
    update_data = {}
    if is_main is not None:
        update_data["is_main"] = is_main
    if sort_order is not None:
        update_data["sort_order"] = sort_order
    
    photo = ProductPhotoService.update_photo(db, photo_id, update_data)
    if photo:
        return {"success": True, "photo": photo}
    else:
        raise HTTPException(status_code=404, detail="Фото не найдено")
