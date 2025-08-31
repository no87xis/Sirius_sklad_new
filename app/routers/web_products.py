from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.products import (
    ProductService, get_products, get_product, update_product, 
    delete_product, create_supply, get_product_supplies
)
from ..schemas.product import ProductCreate, ProductUpdate
from ..schemas.supply import SupplyCreate
from ..deps import require_admin_or_manager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/products", response_class=HTMLResponse)
async def products_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Страница управления складом"""
    products = get_products(db)
    return templates.TemplateResponse(
        "products.html", 
        {"request": request, "current_user": current_user, "products": products}
    )


@router.get("/products/new", response_class=HTMLResponse)
async def new_product_page(
    request: Request,
    current_user = Depends(require_admin_or_manager())
):
    """Страница создания нового товара"""
    return templates.TemplateResponse(
        "products/new.html", 
        {"request": request, "current_user": current_user}
    )


@router.post("/products", response_class=HTMLResponse)
async def create_product_post(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    detailed_description: Optional[str] = Form(None),
    min_stock: int = Form(0),
    buy_price_eur: Optional[str] = Form(None),
    sell_price_rub: Optional[str] = Form(None),
    supplier_name: Optional[str] = Form(None),
    initial_quantity: int = Form(0),
    availability_status: Optional[str] = Form(None),
    expected_date: Optional[str] = Form(None),
    photos: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Создание нового товара"""
    try:
        from decimal import Decimal
        

        
        product_data = ProductCreate(
            name=name,
            description=description,
            detailed_description=detailed_description,
            min_stock=min_stock,
            buy_price_eur=Decimal(buy_price_eur) if buy_price_eur else None,
            sell_price_rub=Decimal(sell_price_rub) if sell_price_rub else None,
            supplier_name=supplier_name,
            initial_quantity=initial_quantity
        )
        
        # Получаем дополнительные поля
        availability_status = availability_status
        expected_date_str = expected_date
        
        # Преобразуем дату если указана
        expected_date_obj = None
        if expected_date_str:
            try:
                expected_date_obj = datetime.strptime(expected_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        # Создаем товар
        product = ProductService.create_product(
            db, 
            product_data, 
            availability_status=availability_status,
            expected_date=expected_date
        )
        
        # Обрабатываем загруженное фото
        if photos and product and photos.filename:
            from ..services.product_photos import ProductPhotoService
            try:
                # Сохраняем фото как главное
                await ProductPhotoService.save_photo(
                    photos, 
                    product.id, 
                    db,
                    is_main=True, 
                    sort_order=0
                )
            except Exception as photo_error:
                # Логируем ошибку, но не прерываем создание товара
                print(f"Ошибка загрузки фото {photos.filename}: {photo_error}")
                # Можно также добавить flash-сообщение об ошибке
        
        return RedirectResponse(
            url="/products?success=Товар успешно создан",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/new?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )











@router.get("/products/{product_id:int}/supplies/new", response_class=HTMLResponse)
async def new_supply_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница создания новой поставки"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return templates.TemplateResponse(
        "supplies/new.html",
        {"request": request, "current_user": current_user, "product": product}
    )


@router.post("/products/{product_id:int}/supplies", response_class=HTMLResponse)
async def create_supply_post(
    request: Request,
    product_id: int,
    qty: int = Form(...),
    supplier_name: str = Form(...),
    buy_price_eur: float = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Создание новой поставки"""
    try:
        supply_data = SupplyCreate(
            product_id=product_id,
            qty=qty,
            supplier_name=supplier_name,
            buy_price_eur=buy_price_eur
        )
        
        create_supply(db, supply_data)
        return RedirectResponse(
            url=f"/products/{product_id}?success=Поставка успешно создана",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/{product_id}/supplies/new?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )





# Параметрические маршруты (после всех статических)
@router.get("/products/{product_id:int}", response_class=HTMLResponse)
async def product_detail_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Страница детальной информации о товаре"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    supplies = get_product_supplies(db, product_id)
    
    return templates.TemplateResponse(
        "products/detail.html",
        {
            "request": request, 
            "current_user": current_user, 
            "product": product,
            "supplies": supplies
        }
    )


@router.get("/products/{product_id:int}/edit", response_class=HTMLResponse)
async def edit_product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Страница редактирования товара"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return templates.TemplateResponse(
        "products/edit.html",
        {"request": request, "current_user": current_user, "product": product}
    )


@router.post("/products/{product_id:int}", response_class=HTMLResponse)
async def update_product_post(
    request: Request,
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    detailed_description: Optional[str] = Form(None),
    min_stock: Optional[int] = Form(None),
    quantity: Optional[int] = Form(None),
    buy_price_eur: Optional[float] = Form(None),
    sell_price_rub: Optional[float] = Form(None),
    supplier_name: Optional[str] = Form(None),
    availability_status: Optional[str] = Form(None),
    expected_date: Optional[str] = Form(None),
    new_photos: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Обновление товара"""
    try:
        # Преобразуем дату из строки
        expected_date_obj = None
        if expected_date:
            from datetime import datetime
            try:
                expected_date_obj = datetime.strptime(expected_date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Ошибка парсинга даты: {expected_date}")
        
        product_data = ProductUpdate(
            name=name,
            description=description,
            detailed_description=detailed_description,
            min_stock=min_stock,
            buy_price_eur=buy_price_eur,
            sell_price_rub=sell_price_rub,
            supplier_name=supplier_name,
            availability_status=availability_status,
            expected_date=expected_date_obj
        )
        
        # Обновляем товар
        update_product(db, product_id, product_data)
        
        # Обновляем количество товара отдельно (если указано)
        if quantity is not None:
            from ..services.products import update_product_quantity
            update_product_quantity(db, product_id, quantity)
        
        # Обрабатываем новое загруженное фото
        if new_photos and product_id and new_photos.filename:
            from ..services.product_photos import ProductPhotoService
            try:
                # Сохраняем фото (не делаем главным)
                await ProductPhotoService.save_photo(
                    new_photos, 
                    product_id, 
                    db,
                    is_main=False, 
                    sort_order=0
                )
            except Exception as photo_error:
                # Логируем ошибку, но не прерываем обновление товара
                print(f"Ошибка загрузки фото {new_photos.filename}: {photo_error}")
        
        return RedirectResponse(
            url=f"/products/{product_id}?success=Товар успешно обновлен",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/{product_id}/edit?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/products/{product_id:int}/delete", response_class=HTMLResponse)
async def delete_product_post(
    request: Request,
    product_id: int,
    force: bool = Form(False),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Удаление товара"""
    try:
        delete_product(db, product_id, force=force)
        message = "Товар успешно удален" if not force else "Товар принудительно удален (с активными заказами)"
        return RedirectResponse(
            url=f"/products?success={message}",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/{product_id}?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )
