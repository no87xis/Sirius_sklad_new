from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.auth import get_current_user_optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/qr-scanner", response_class=HTMLResponse)
async def qr_scanner_page(request: Request, db: Session = Depends(get_db)):
    """Страница QR-сканера"""
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse("qr_scanner.html", {"request": request, "current_user": current_user})
