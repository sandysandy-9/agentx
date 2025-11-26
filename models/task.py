from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
from uuid import uuid4


class Task(BaseModel):
    """Task model for task management system"""
    
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = []
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project report",
                "description": "Write and submit the final B.Tech project report",
                "priority": "high",
                "deadline": "2025-12-01T23:59:59",
                "category": "academics",
                "tags": ["urgent", "school"],
                "status": "pending"
            }
        }


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = []


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
