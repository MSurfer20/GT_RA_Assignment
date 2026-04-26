# File for defining database models using ORM

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, TypeDecorator
from sqlalchemy.sql import func
from datetime import timezone
from .database import Base

class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None:
            # SQLite returns naive datetimes. Force it to be UTC aware.
            return value.replace(tzinfo=timezone.utc)
        return value

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, index=True, nullable=True)
    status = Column(String, default="Pending")
    
    created_at = Column(UTCDateTime, server_default=func.now())
    updated_at = Column(UTCDateTime, onupdate=func.now())
    

    record_count = Column(Integer, nullable=True)
    category_summary = Column(JSON, nullable=True)
    average_value = Column(Float, nullable=True)
    invalid_records = Column(Integer, nullable=True)
    
    error_message = Column(String, nullable=True)
    
