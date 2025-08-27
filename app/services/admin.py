from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import User, OperationLog, UserRole
from ..schemas.user import UserUpdate, UserCreate
from ..services.auth import get_password_hash

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Получить список всех пользователей"""
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID (устаревшая функция)"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получить пользователя по имени пользователя"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """Создать нового пользователя"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, username: str, user_data: UserUpdate) -> Optional[User]:
    """Обновить пользователя"""
    db_user = get_user_by_username(db, username)
    if not db_user:
        return None
    
    if user_data.username is not None:
        db_user.username = user_data.username
    if user_data.role is not None:
        db_user.role = user_data.role
    if user_data.password is not None:
        db_user.hashed_password = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, username: str) -> bool:
    """Удалить пользователя"""
    db_user = get_user_by_username(db, username)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def get_user_statistics(db: Session) -> Dict[str, Any]:
    """Получить статистику по пользователям"""
    total_users = db.query(func.count(User.username)).scalar()
    
    # Статистика по ролям
    role_stats = db.query(
        User.role,
        func.count(User.username).label('count')
    ).group_by(User.role).all()
    
    role_counts = {role: count for role, count in role_stats}
    
    return {
        'total_users': total_users,
        'role_counts': role_counts,
        'admin_count': role_counts.get(UserRole.ADMIN, 0),
        'manager_count': role_counts.get(UserRole.MANAGER, 0),
        'user_count': role_counts.get(UserRole.USER, 0)
    }

def get_operation_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[OperationLog]:
    """Получить логи операций с фильтрацией"""
    query = db.query(OperationLog)
    
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if operation_type:
        query = query.filter(OperationLog.action == operation_type)
    if start_date:
        query = query.filter(OperationLog.timestamp >= start_date)
    if end_date:
        query = query.filter(OperationLog.timestamp <= end_date)
    
    return query.order_by(desc(OperationLog.timestamp)).offset(skip).limit(limit).all()

def get_log_statistics(db: Session) -> Dict[str, Any]:
    """Получить статистику по логам"""
    total_logs = db.query(func.count(OperationLog.id)).scalar()
    
    # Статистика по типам операций
    operation_stats = db.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    ).group_by(OperationLog.action).all()
    
    operation_counts = {op_type: count for op_type, count in operation_stats}
    
    # Статистика по пользователям
    user_stats = db.query(
        OperationLog.user_id,
        func.count(OperationLog.id).label('count')
    ).group_by(OperationLog.user_id).all()
    
    user_counts = {user_id: count for user_id, count in user_stats}
    
    # Логи за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    recent_logs = db.query(func.count(OperationLog.id)).filter(
        OperationLog.timestamp >= week_ago
    ).scalar()
    
    return {
        'total_logs': total_logs,
        'operation_counts': operation_counts,
        'user_counts': user_counts,
        'recent_logs': recent_logs
    }

def create_operation_log(
    db: Session,
    user_id: str,
    operation_type: str,
    details: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None
) -> OperationLog:
    """Создать запись в логе операций"""
    log_entry = OperationLog(
        user_id=user_id,
        action=operation_type,
        details=details,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
