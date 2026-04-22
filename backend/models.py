# File for defining database models using ORM

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, index=True, nullable=True)
    status = Column(String, default="Pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

    record_count = Column(Integer, nullable=True)
    category_summary = Column(JSON, nullable=True)
    average_value = Column(Float, nullable=True)
    invalid_records = Column(Integer, nullable=True)
    
