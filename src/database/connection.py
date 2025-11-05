"""
Database connection management using SQLAlchemy.
Provides engine creation and session management for SQL Server.
"""

from contextlib import contextmanager
from typing import Generator

from loguru import logger
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from src.config.settings import settings


def create_db_engine(read_only: bool = True) -> Engine:
    """
    Create SQLAlchemy engine for SQL Server with Windows Authentication.

    Args:
        read_only: If True, enforce READ-ONLY mode on connections (default: True)

    Returns:
        SQLAlchemy Engine instance

    Raises:
        Exception: If engine creation fails
    """
    try:
        logger.info(f"Creating database engine for {settings.db_server}/{settings.db_name} (read_only={read_only})")

        engine = create_engine(
            settings.database_url,
            echo=settings.log_level == "DEBUG",
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"timeout": settings.db_timeout},
        )

        # Add event listener for connection
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")

            # Enforce READ-ONLY mode if requested
            if read_only:
                cursor = dbapi_conn.cursor()
                try:
                    # Set connection to READ-ONLY mode (SQL Server 2014+ compatible)
                    cursor.execute("SET TRANSACTION READ ONLY")
                    logger.debug("Database connection set to READ-ONLY mode")
                except Exception as e:
                    logger.warning(f"Failed to set READ-ONLY mode: {e}")
                finally:
                    cursor.close()

        logger.info("Database engine created successfully")
        return engine

    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def test_connection(engine: Engine) -> bool:
    """
    Test database connection by executing a simple query.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            logger.info(f"Database connection test successful: {row}")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_session_factory(engine: Engine) -> sessionmaker:
    """
    Create a session factory for database operations.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        Session factory
    """
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db_session(engine: Engine) -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Args:
        engine: SQLAlchemy Engine instance

    Yields:
        Database session

    Usage:
        with get_db_session(engine) as session:
            # Use session
            pass
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


# Global engine instance (created lazily)
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Get or create the global database engine.

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session using the global engine.

    Yields:
        Database session

    Usage:
        with get_session() as session:
            # Use session
            pass
    """
    engine = get_engine()
    yield from get_db_session(engine)


def close_engine() -> None:
    """
    Close the global database engine and all connections.
    """
    global _engine
    if _engine is not None:
        logger.info("Closing database engine")
        _engine.dispose()
        _engine = None
