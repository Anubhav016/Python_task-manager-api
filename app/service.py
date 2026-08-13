"""
Service layer — business rules live here, not in the routes or the repository.

Routes should never talk to the repository directly. That indirection is
what makes it possible to, e.g., add a rule like "can't mark a task done
without a description" in exactly one place, and to unit-test that rule
without spinning up HTTP at all (see tests/test_tasks.py).
"""
from typing import Optional

from app.models import Task, TaskStatus
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a task_id doesn't exist. Routes translate this to a 404."""
    pass


class InvalidTransitionError(Exception):
    """Raised when a status change breaks a business rule. Routes -> 400."""
    pass


# Tasks can only move forward through this pipeline, and never skip
# in_progress on the way to done. This is the "business rule" a repository
# alone could never enforce.
_ALLOWED_TRANSITIONS = {
    TaskStatus.pending: {TaskStatus.in_progress},
    TaskStatus.in_progress: {TaskStatus.done, TaskStatus.pending},
    TaskStatus.done: set(),  # done is terminal
}


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, payload: TaskCreate) -> Task:
        return self.repository.create(
            title=payload.title.strip(),
            description=payload.description,
            status=payload.status,
        )

    def get_task(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(self, status: Optional[TaskStatus], skip: int, limit: int) -> list[Task]:
        return self.repository.list(status=status, skip=skip, limit=limit)

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        task = self.get_task(task_id)  # raises TaskNotFoundError if missing

        if payload.status is not None and payload.status != task.status:
            if payload.status not in _ALLOWED_TRANSITIONS[task.status]:
                raise InvalidTransitionError(
                    f"Cannot move task from '{task.status.value}' to '{payload.status.value}'"
                )

        return self.repository.update(
            task,
            title=payload.title,
            description=payload.description,
            status=payload.status,
        )

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.repository.delete(task)
