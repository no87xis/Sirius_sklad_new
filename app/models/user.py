from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class User(Base):
    __tablename__ = "users"
    
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связи
    orders = relationship("Order", back_populates="user")
