from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.products import (
    get_products, get_product, create_product, update_product, 
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
    min_stock: int = Form(0),
    buy_price_eur: Optional[float] = Form(None),
    sell_price_rub: Optional[float] = Form(None),
    supplier_name: Optional[str] = Form(None),
    initial_quantity: int = Form(0),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Создание нового товара"""
    try:
        product_data = ProductCreate(
            name=name,
            description=description,
            min_stock=min_stock,
            buy_price_eur=buy_price_eur,
            sell_price_rub=sell_price_rub,
            supplier_name=supplier_name,
            initial_quantity=initial_quantity
        )
        
        create_product(db, product_data)
        return RedirectResponse(
            url="/products?success=Товар успешно создан",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/new?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )





@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
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


@router.post("/products/{product_id}", response_class=HTMLResponse)
async def update_product_post(
    request: Request,
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    min_stock: Optional[int] = Form(None),
    buy_price_eur: Optional[float] = Form(None),
    sell_price_rub: Optional[float] = Form(None),
    supplier_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Обновление товара"""
    try:
        product_data = ProductUpdate(
            name=name,
            description=description,
            min_stock=min_stock,
            buy_price_eur=buy_price_eur,
            sell_price_rub=sell_price_rub,
            supplier_name=supplier_name
        )
        
        update_product(db, product_id, product_data)
        return RedirectResponse(
            url=f"/products/{product_id}?success=Товар успешно обновлен",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/{product_id}/edit?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/products/{product_id}/delete", response_class=HTMLResponse)
async def delete_product_post(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager())
):
    """Удаление товара"""
    try:
        delete_product(db, product_id)
        return RedirectResponse(
            url="/products?success=Товар успешно удален",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/products/{product_id}?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )





@router.get("/products/{product_id}/supplies/new", response_class=HTMLResponse)
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


@router.post("/products/{product_id}/supplies", response_class=HTMLResponse)
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


@router.get("/products/{product_id}", response_class=HTMLResponse)
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
