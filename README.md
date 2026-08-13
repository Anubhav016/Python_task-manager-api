# Task Manager API

A small RESTful CRUD API for managing tasks, built with FastAPI and SQLAlchemy,
structured with a **layered architecture** (routes → service → repository)
and covered by unit + integration tests with pytest.

## Why layered architecture

Most tutorial CRUD APIs put database queries directly inside route handlers.
This project deliberately separates concerns into three layers:

| Layer | File | Responsibility |
|---|---|---|
| **Routes** | `app/routes.py` | HTTP only — parses requests, maps service exceptions to status codes |
| **Service** | `app/service.py` | Business rules (e.g. a task can't jump from `pending` straight to `done`) |
| **Repository** | `app/repository.py` | Raw data access — the only place that talks SQLAlchemy |

This means business rules can be unit-tested without spinning up HTTP
(`tests/test_service.py`), and the repository could be swapped for a
different database or an in-memory fake without touching business logic.

## Features

- Full CRUD on tasks (create, list with filtering, get, partial update, delete)
- Enforced status workflow: `pending → in_progress → done` (no skipping stages)
- Request/response validation via Pydantic
- Auto-generated interactive API docs (Swagger UI) at `/docs`
- 13 tests covering business rules and HTTP contract

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for interactive Swagger UI, or:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Build a CRUD API"}'

curl http://127.0.0.1:8000/tasks
```

## Run tests

```bash
pytest -v
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks (optional `?status=pending` filter, `skip`/`limit` pagination) |
| GET | `/tasks/{id}` | Get one task |
| PATCH | `/tasks/{id}` | Partially update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## Project structure

```
app/
  main.py        # FastAPI app entrypoint
  database.py     # Engine/session setup
  models.py       # SQLAlchemy ORM models
  schemas.py      # Pydantic request/response schemas
  repository.py   # Data access layer
  service.py      # Business logic layer
  routes.py       # HTTP route handlers
tests/
  conftest.py     # Shared fixtures (isolated in-memory test DB)
  test_service.py # Unit tests for business rules
  test_api.py     # Integration tests through the HTTP layer
```

## Possible extensions

- Swap `create_all` for Alembic migrations
- Add user auth (JWT) and per-user task ownership
- Add due dates + a `/tasks?overdue=true` filter
- Containerize with Docker
