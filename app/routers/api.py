from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "ok", "message": "API работает"}
