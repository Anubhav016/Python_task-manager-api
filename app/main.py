"""
App entrypoint. Run with:  uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs for interactive Swagger UI.
"""
from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router as tasks_router

# Creates tasks.db and the tasks table on first run if they don't exist yet.
# (Fine for a small project like this; a real production app would use
# Alembic migrations instead of create_all.)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="A small CRUD API demonstrating layered architecture "
                 "(routes -> service -> repository) in FastAPI.",
    version="1.0.0",
)

app.include_router(tasks_router)


@app.get("/")
def root():
    return {"message": "Task Manager API is running. See /docs for the API reference."}
