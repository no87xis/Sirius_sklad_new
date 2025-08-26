from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from ..db import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(String, nullable=True)  # nullable для системных операций
    action = Column(String, nullable=False)  # create, update, delete, issue, deny
    entity_type = Column(String, nullable=False)  # user, product, order, supply
    entity_id = Column(String, nullable=False)  # ID сущности
    details = Column(Text, nullable=True)  # дополнительные детали в JSON или тексте
