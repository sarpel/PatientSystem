"""
Separate application database for ICD codes, sessions, and logs.
Uses SQLite for simplicity and portability.
The main MSSQL database remains READ-ONLY.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from loguru import logger
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.sql import func

# Base for app-specific models
AppBase = declarative_base()


class ICDCode(AppBase):
    """ICD-10 code mappings table."""
    __tablename__ = "icd_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    diagnosis_name_en = Column(String(255), nullable=False, index=True)
    diagnosis_name_tr = Column(String(255))
    category = Column(String(100), index=True)
    icd_version = Column(String(10), default="ICD-10")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AppLog(AppBase):
    """Application logs table."""
    __tablename__ = "app_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(255))
    function = Column(String(255))
    created_at = Column(DateTime, default=func.now(), index=True)


class AppSession(AppBase):
    """Application session tracking table."""
    __tablename__ = "app_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255))
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    session_data = Column(Text)  # JSON serialized session data (renamed from metadata)


def create_app_db_engine(db_path: str = "data/app.db") -> Engine:
    """
    Create SQLAlchemy engine for application SQLite database.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy Engine instance
    """
    try:
        # Ensure data directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating app database engine at {db_path}")

        engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},  # Allow multi-threading
        )

        # Create tables if they don't exist
        AppBase.metadata.create_all(engine)

        logger.info("App database engine created successfully")
        return engine

    except Exception as e:
        logger.error(f"Failed to create app database engine: {e}")
        raise


def get_app_session_factory(engine: Engine) -> sessionmaker:
    """
    Create a session factory for app database operations.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        Session factory
    """
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_app_session(engine: Engine) -> Generator[Session, None, None]:
    """
    Get an app database session.

    Args:
        engine: SQLAlchemy Engine instance

    Yields:
        Database session
    """
    SessionLocal = get_app_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Global app engine instance
_app_engine: Engine | None = None


def get_app_engine(db_path: str = "data/app.db") -> Engine:
    """
    Get or create the global app database engine.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy Engine instance
    """
    global _app_engine
    if _app_engine is None:
        _app_engine = create_app_db_engine(db_path)
    return _app_engine


@contextmanager
def get_app_db_session(db_path: str = "data/app.db") -> Generator[Session, None, None]:
    """
    Get an app database session using the global engine.

    Args:
        db_path: Path to SQLite database file

    Yields:
        Database session
    """
    engine = get_app_engine(db_path)
    SessionLocal = get_app_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def close_app_engine() -> None:
    """Close the global app database engine."""
    global _app_engine
    if _app_engine is not None:
        logger.info("Closing app database engine")
        _app_engine.dispose()
        _app_engine = None
