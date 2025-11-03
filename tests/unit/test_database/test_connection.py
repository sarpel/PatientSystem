"""
Unit tests for database connection module.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.config.settings import settings
from src.database.connection import (
    create_db_engine,
    get_engine,
    get_session_factory,
    test_connection,
)


class TestDatabaseConnection:
    """Test database connection functionality."""

    def test_settings_loaded(self):
        """Test that settings are loaded correctly."""
        assert settings.db_server is not None
        assert settings.db_name is not None
        assert settings.db_driver is not None

    def test_database_url_format(self):
        """Test that database URL is formatted correctly."""
        db_url = settings.database_url
        assert db_url.startswith("mssql+pyodbc://")
        assert "odbc_connect=" in db_url
        assert settings.db_server.replace("\\", "%5C") in db_url or settings.db_server in db_url

    def test_create_engine(self):
        """Test engine creation."""
        engine = create_db_engine()
        assert isinstance(engine, Engine)
        assert engine is not None

    def test_connection_test(self):
        """Test database connection."""
        engine = get_engine()
        result = test_connection(engine)
        assert result is True, "Database connection test failed"

    def test_execute_query(self):
        """Test executing a simple query."""
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION AS version"))
            row = result.fetchone()
            assert row is not None
            assert "Microsoft SQL Server" in str(row[0])

    def test_session_factory(self):
        """Test session factory creation."""
        engine = get_engine()
        SessionLocal = get_session_factory(engine)
        assert SessionLocal is not None

        session = SessionLocal()
        assert session is not None
        session.close()


if __name__ == "__main__":
    # Run tests manually
    test = TestDatabaseConnection()
    print("Testing settings loaded...")
    test.test_settings_loaded()
    print("✓ Settings loaded")

    print("\nTesting database URL format...")
    test.test_database_url_format()
    print("✓ Database URL format correct")

    print("\nTesting engine creation...")
    test.test_create_engine()
    print("✓ Engine created")

    print("\nTesting database connection...")
    test.test_connection_test()
    print("✓ Database connection successful")

    print("\nTesting query execution...")
    test.test_execute_query()
    print("✓ Query executed successfully")

    print("\nTesting session factory...")
    test.test_session_factory()
    print("✓ Session factory works")

    print("\n✅ All tests passed!")
