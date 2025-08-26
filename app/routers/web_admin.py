from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/analytics")
async def analytics_page(request: Request):
    """Страница аналитики (заглушка)"""
    return templates.TemplateResponse("admin/analytics.html", {"request": request})
