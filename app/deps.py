from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .db import get_db
from .models import User, UserRole
from .services.auth import get_current_user, get_current_user_optional


def require_role(required_role: UserRole):
    """Зависимость для проверки роли пользователя"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return current_user
    return role_checker


def require_admin():
    """Зависимость для проверки роли админа"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return current_user
    return role_checker


def require_admin_or_manager():
    """Зависимость для проверки роли admin или manager"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return current_user
    return role_checker
