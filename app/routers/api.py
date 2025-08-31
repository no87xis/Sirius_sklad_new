from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.product_photos import ProductPhotoService
from ..services.monitoring import performance_monitor

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


@router.get("/metrics/performance")
async def get_performance_metrics():
    """Получить метрики производительности"""
    try:
        metrics = performance_monitor.get_performance_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/metrics/slow-queries")
async def get_slow_queries(threshold: float = 1.0):
    """Получить медленные запросы"""
    try:
        slow_queries = performance_monitor.get_slow_queries(threshold)
        return {
            "status": "success",
            "data": {
                "threshold": threshold,
                "count": len(slow_queries),
                "queries": slow_queries
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/metrics/errors")
async def get_error_summary():
    """Получить сводку по ошибкам"""
    try:
        error_summary = performance_monitor.get_error_summary()
        return {
            "status": "success",
            "data": error_summary
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/metrics/reset")
async def reset_performance_metrics():
    """Сбросить метрики производительности"""
    try:
        performance_monitor.reset_metrics()
        return {
            "status": "success",
            "message": "Метрики производительности сброшены"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
