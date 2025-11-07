"""
Test database connection to SQL Server
Tests both localhost and computer name connection strings
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from sqlalchemy import create_engine, text

# Test configurations
TESTS = [
    {
        "name": "localhost with HIZIR instance",
        "url": "mssql+pyodbc://localhost\\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes",
    },
    {
        "name": "SARPEL-PC with HIZIR instance",
        "url": "mssql+pyodbc://SARPEL-PC\\HIZIR/TestDB?driver=ODBC+Driver+11+for+SQL+Server&trusted_connection=yes",
    },
]

def test_connection(config):
    """Test a single database connection configuration."""
    logger.info(f"Testing: {config['name']}")

    try:
        # Create engine
        engine = create_engine(
            config["url"],
            echo=False,
            pool_pre_ping=True,
            connect_args={"timeout": 10}
        )

        # Test connection
        with engine.connect() as conn:
            # Basic query
            result = conn.execute(text("SELECT 1 AS test"))
            _ = result.fetchone()  # Consume result

            # Get server info
            server_info = conn.execute(text("SELECT @@VERSION AS version"))
            version = server_info.fetchone()[0]

            # Get database name
            db_name = conn.execute(text("SELECT DB_NAME() AS db"))
            db = db_name.fetchone()[0]

            # Get user
            user_info = conn.execute(text("SELECT SYSTEM_USER AS username"))
            user = user_info.fetchone()[0]

            logger.success(f"✅ Connection successful!")
            logger.info(f"   Database: {db}")
            logger.info(f"   User: {user}")
            version_line = version.split('\n')[0]
            logger.info(f"   Version: {version_line}")

            return True

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False
    finally:
        try:
            engine.dispose()
        except Exception:
            # Ignore disposal errors
            pass

def main():
    """Run all connection tests."""
    logger.info("=" * 60)
    logger.info("SQL Server Connection Tests")
    logger.info("=" * 60)

    results = []
    for config in TESTS:
        success = test_connection(config)
        results.append((config["name"], success))
        logger.info("-" * 60)

    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary:")
    logger.info("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {name}")

    successful = sum(1 for _, success in results if success)
    logger.info(f"\nTotal: {successful}/{len(results)} tests passed")

    if successful > 0:
        logger.success("\n🎉 At least one connection method works!")
        logger.info("\nRecommended connection string for .env:")
        for name, success in results:
            if success:
                matching_config = next(c for c in TESTS if c["name"] == name)
                logger.info(f"\nDATABASE_URL={matching_config['url']}")
                break
    else:
        logger.error("\n❌ No connections succeeded. Please check:")
        logger.error("   1. SQL Server service is running")
        logger.error("   2. ODBC Driver 17 or 18 is installed")
        logger.error("   3. Windows Authentication is enabled")
        logger.error("   4. TestDB database exists")

if __name__ == "__main__":
    main()
