import os
from typing import Optional
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Конфигурация для тестового окружения"""
    
    # Тестовая база данных
    database_url: str = "sqlite:///./test.db"
    
    # Тестовые ключи
    secret_key: str = "test-secret-key-for-testing-only-32-chars"
    session_max_age: int = 3600  # 1 час для тестов
    
    # Тестовое окружение
    environment: str = "testing"
    debug: bool = True
    
    # Отключаем внешние сервисы для тестов
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env.test"
        case_sensitive = False


test_settings = TestSettings()
