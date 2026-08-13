"""
HTTP layer — translates HTTP requests into service calls, and service
exceptions into proper HTTP status codes. No business logic lives here.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TaskStatus
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.service import InvalidTransitionError, TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_service)):
    return service.create_task(payload)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: TaskService = Depends(get_service),
):
    return service.list_tasks(status=status_filter, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    try:
        return service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, service: TaskService = Depends(get_service)):
    try:
        return service.update_task(task_id, payload)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
