import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sirius.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    session_max_age: int = 86400  # 24 hours
    
    # Telegram notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Email (optional)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
