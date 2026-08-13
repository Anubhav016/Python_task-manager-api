"""
Repository layer — the ONLY place in the app that speaks SQLAlchemy/SQL.

Deliberately "dumb": it knows how to fetch/insert/update/delete rows, and
nothing about business rules. This is what makes the service layer (and its
tests) able to swap this out for a fake/in-memory repository without
touching any business logic.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, description: Optional[str], status: TaskStatus) -> Task:
        task = Task(title=title, description=description, status=status)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list(self, status: Optional[TaskStatus] = None,
              skip: int = 0, limit: int = 100) -> list[Task]:
        query = self.db.query(Task)
        if status is not None:
            query = query.filter(Task.status == status)
        return query.order_by(Task.id).offset(skip).limit(limit).all()

    def update(self, task: Task, **fields) -> Task:
        for key, value in fields.items():
            if value is not None:
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
