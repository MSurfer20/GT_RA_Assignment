from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TaskResponse(BaseModel):
    id: str
    dataset_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    record_count: Optional[int] = None
    category_summary: Optional[Dict[str, int]] = None
    average_value: Optional[float] = None
    invalid_records: Optional[int] = None
    
    class Config:
        from_attributes = True
