from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, Depends
from ..models import User
from ..db import get_db

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хэширование пароля"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Получить текущего пользователя из сессии"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Получить текущего пользователя (опционально)"""
    user_id = request.session.get("user_id")
    print(f"🔍 Проверка сессии: user_id={user_id}, session={dict(request.session)}")  # Отладочная информация
    
    if not user_id:
        return None
    
    user = db.query(User).filter(User.username == user_id).first()
    if user:
        print(f"✅ Пользователь найден: {user.username}")
    else:
        print(f"❌ Пользователь не найден для user_id: {user_id}")
    
    return user


def create_user(db: Session, username: str, password: str, role: str = "user") -> User:
    """Создание нового пользователя"""
    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Создание пользователя
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        hashed_password=hashed_password,
        role=role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
