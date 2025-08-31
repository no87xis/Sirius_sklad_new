from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..db import get_db
from ..services.auth import get_current_user_optional
from ..services.validation import ValidationService


class BaseRouter:
    """Базовый класс для всех роутеров"""
    
    def __init__(self, prefix: str = "", tags: Optional[list] = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self.templates = Jinja2Templates(directory="app/templates")
        self.validation = ValidationService()
    
    def get_current_user_safe(self, request: Request, db: Session) -> Optional[Any]:
        """Безопасное получение текущего пользователя"""
        try:
            return get_current_user_optional(request, db)
        except Exception:
            return None
    
    def render_template(self, template_name: str, request: Request, context: Dict[str, Any]) -> HTMLResponse:
        """Безопасный рендеринг шаблона"""
        try:
            # Добавляем базовый контекст
            base_context = {
                "request": request,
                "current_user": context.get("current_user"),
                "error_message": context.get("error_message"),
                "success_message": context.get("success_message")
            }
            base_context.update(context)
            
            return self.templates.TemplateResponse(template_name, base_context)
        except Exception as e:
            # Логируем ошибку и возвращаем базовую страницу
            print(f"Ошибка рендеринга шаблона {template_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка отображения страницы"
            )
    
    def validate_and_sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация и очистка входных данных"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.validation.sanitize_input(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def handle_database_error(self, error: Exception, operation: str = "операция"):
        """Обработка ошибок базы данных"""
        print(f"Ошибка БД при {operation}: {error}")
        
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Запись с такими данными уже существует"
            )
        elif "FOREIGN KEY constraint failed" in str(error):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Связанная запись не найдена"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка базы данных при {operation}"
            )
