"""
ORM models — the shape of data as it lives in the database.

Kept separate from schemas.py (the API's request/response shape) on purpose:
the DB representation and the API contract are allowed to evolve
independently. Mixing them is a common beginner mistake this project
deliberately avoids.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func

from app.database import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
