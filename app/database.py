"""
Database configuration.

Uses SQLite for simplicity (zero setup), but because we go through
SQLAlchemy's engine/session abstraction, swapping to Postgres/MySQL later
only means changing DATABASE_URL — nothing else in the app needs to change.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./tasks.db"

# check_same_thread=False is only needed for SQLite (FastAPI can hit the
# same connection from different threads); other DBs don't need this arg.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees it's closed
    afterwards, even if the request raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
