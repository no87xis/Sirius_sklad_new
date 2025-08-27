from pydantic import BaseModel, ConfigDict
from typing import Optional
from ..models import UserRole

class UserBase(BaseModel):
    username: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    username: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
