from fastapi import Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from ..services.logger import logger
from ..config import settings
from datetime import datetime


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки ошибок"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Логируем ошибку
            logger.log_error(
                exc, 
                context=f"HTTP {request.method} {request.url.path}",
                user_id=request.session.get("user_id") if hasattr(request, 'session') else None
            )
            
            # Определяем тип ответа
            accept_header = request.headers.get("accept", "")
            is_html_request = "text/html" in accept_header
            
            if is_html_request:
                # Для HTML запросов возвращаем страницу ошибки
                return HTMLResponse(
                    content=self._get_error_html(exc),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                # Для API запросов возвращаем JSON
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": "Внутренняя ошибка сервера",
                        "detail": str(exc) if settings.debug else "Произошла ошибка",
                        "timestamp": str(datetime.now())
                    }
                )
    
    def _get_error_html(self, error: Exception) -> str:
        """Генерирует HTML страницу ошибки"""
        return f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ошибка - Сириус</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-container {{ max-width: 600px; margin: 0 auto; }}
                .error-code {{ font-size: 72px; color: #e74c3c; margin: 0; }}
                .error-message {{ font-size: 24px; color: #2c3e50; margin: 20px 0; }}
                .error-detail {{ color: #7f8c8d; margin: 20px 0; }}
                .back-button {{ 
                    background: #3498db; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block; 
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1 class="error-code">500</h1>
                <h2 class="error-message">Внутренняя ошибка сервера</h2>
                <p class="error-detail">
                    Произошла непредвиденная ошибка. Попробуйте обновить страницу или вернуться на главную.
                </p>
                {f'<p class="error-detail">Детали: {str(error)}</p>' if settings.debug else ''}
                <a href="/" class="back-button">Вернуться на главную</a>
            </div>
        </body>
        </html>
        """


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""
    
    async def dispatch(self, request: Request, call_next):
        # Логируем входящий запрос
        logger.log_request({
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "UNKNOWN",
            "headers": dict(request.headers)
        }, request.session.get("user_id") if hasattr(request, 'session') else None)
        
        response = await call_next(request)
        return response
