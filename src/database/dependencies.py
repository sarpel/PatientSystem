"""
FastAPI dependency injection for database sessions.
Provides proper session lifecycle management for multi-process deployments.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.connection import create_db_engine, get_session_factory


def get_db_engine():
    """
    FastAPI dependency to get database engine.
    Creates engine per worker process for multi-process deployment safety.

    Yields:
        SQLAlchemy Engine instance
    """
    engine = create_db_engine()
    try:
        yield engine
    finally:
        engine.dispose()


def get_db(engine=Depends(get_db_engine)) -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.
    Handles automatic commit/rollback and session cleanup.

    Args:
        engine: SQLAlchemy engine (injected by FastAPI)

    Yields:
        Database session
    """
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
