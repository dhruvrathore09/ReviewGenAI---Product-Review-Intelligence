"""Database session dependency injection for FastAPI."""

from typing import Generator
from sqlalchemy.orm import Session
from src.db.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields an active database session and ensures it closes after request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

