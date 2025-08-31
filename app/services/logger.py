import logging
import sys
from datetime import datetime
from pathlib import Path
from ..config import settings


class LoggerService:
    """Централизованная система логирования"""
    
    def __init__(self):
        self.logger = logging.getLogger("sirius")
        self.logger.setLevel(logging.INFO)
        
        # Создаем директорию для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Хендлер для файла
        file_handler = logging.FileHandler(
            log_dir / f"sirius_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Хендлер для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO if not settings.debug else logging.DEBUG)
        
        # Добавляем хендлеры
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Отключаем дублирование логов
        self.logger.propagate = False
    
    def info(self, message: str, **kwargs):
        """Информационное сообщение"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Сообщение об ошибке"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Предупреждение"""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Отладочное сообщение"""
        if settings.debug:
            self.logger.debug(message, extra=kwargs)
    
    def log_request(self, request: dict, user_id: str = None):
        """Логирование HTTP запросов"""
        self.info(
            f"HTTP {request.get('method', 'UNKNOWN')} {request.get('url', 'UNKNOWN')}",
            user_id=user_id,
            ip=request.get('client', 'UNKNOWN'),
            user_agent=request.get('headers', {}).get('user-agent', 'UNKNOWN')
        )
    
    def log_error(self, error: Exception, context: str = "", user_id: str = None):
        """Логирование ошибок"""
        self.error(
            f"Ошибка в {context}: {str(error)}",
            error_type=type(error).__name__,
            user_id=user_id,
            traceback=str(error)
        )
    
    def log_database_operation(self, operation: str, table: str, user_id: str = None):
        """Логирование операций с БД"""
        self.info(
            f"DB операция: {operation} в таблице {table}",
            operation=operation,
            table=table,
            user_id=user_id
        )


# Создаем глобальный экземпляр логгера
logger = LoggerService()
