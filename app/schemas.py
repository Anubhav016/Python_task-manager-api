"""
Pydantic schemas — define and validate the API's request/response contract.

Three separate shapes on purpose:
- TaskCreate: what a client is allowed to send when creating a task
- TaskUpdate: what a client is allowed to send when updating (all optional —
  supports partial updates via PATCH)
- TaskOut: what the API sends back (includes server-generated fields like id,
  timestamps — a client should never be able to set these itself)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    # Lets Pydantic read attributes off the SQLAlchemy ORM object directly
    # (task.title) instead of requiring a dict.
    model_config = ConfigDict(from_attributes=True)
