"""
Unit tests for TaskService — the business-rule layer.

These go through the repository (backed by a real, but in-memory, DB session)
rather than mocking it, which keeps the tests honest about how the layers
actually interact while still being fast (no HTTP involved).
"""
import pytest

from app.models import TaskStatus
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate
from app.service import InvalidTransitionError, TaskNotFoundError, TaskService


@pytest.fixture()
def service(db_session):
    return TaskService(TaskRepository(db_session))


def test_create_task_defaults_to_pending(service):
    task = service.create_task(TaskCreate(title="Write unit tests"))
    assert task.status == TaskStatus.pending
    assert task.id is not None


def test_create_task_strips_whitespace_from_title(service):
    task = service.create_task(TaskCreate(title="  Ship the API  "))
    assert task.title == "Ship the API"


def test_get_task_raises_when_missing(service):
    with pytest.raises(TaskNotFoundError):
        service.get_task(9999)


def test_valid_status_transition_pending_to_in_progress(service):
    task = service.create_task(TaskCreate(title="Deploy"))
    updated = service.update_task(task.id, TaskUpdate(status=TaskStatus.in_progress))
    assert updated.status == TaskStatus.in_progress


def test_invalid_status_transition_pending_to_done(service):
    """Business rule: a task can't skip straight from pending to done."""
    task = service.create_task(TaskCreate(title="Deploy"))
    with pytest.raises(InvalidTransitionError):
        service.update_task(task.id, TaskUpdate(status=TaskStatus.done))


def test_done_is_terminal(service):
    task = service.create_task(TaskCreate(title="Deploy"))
    service.update_task(task.id, TaskUpdate(status=TaskStatus.in_progress))
    service.update_task(task.id, TaskUpdate(status=TaskStatus.done))
    with pytest.raises(InvalidTransitionError):
        service.update_task(task.id, TaskUpdate(status=TaskStatus.in_progress))


def test_list_tasks_filters_by_status(service):
    service.create_task(TaskCreate(title="A"))
    b = service.create_task(TaskCreate(title="B"))
    service.update_task(b.id, TaskUpdate(status=TaskStatus.in_progress))

    pending = service.list_tasks(status=TaskStatus.pending, skip=0, limit=100)
    in_progress = service.list_tasks(status=TaskStatus.in_progress, skip=0, limit=100)

    assert len(pending) == 1
    assert len(in_progress) == 1
    assert pending[0].title == "A"


def test_delete_task_removes_it(service):
    task = service.create_task(TaskCreate(title="Temp"))
    service.delete_task(task.id)
    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)
