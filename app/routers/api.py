from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.product_photos import ProductPhotoService

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "ok", "message": "API работает"}


@router.delete("/photos/{photo_id:int}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Удаляет фотографию товара"""
    try:
        success = ProductPhotoService.delete_photo(db, photo_id)
        if success:
            return {"success": True, "message": "Фотография успешно удалена"}
        else:
            return {"success": False, "message": "Фотография не найдена"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка при удалении: {str(e)}"}
