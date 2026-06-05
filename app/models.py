from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be blank")
        return value


class Task(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime


class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
