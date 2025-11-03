"""Simple database connection test script."""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text

from src.config.settings import settings
from src.database.connection import create_db_engine, test_connection

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

print(f"\n1. Settings loaded:")
print(f"   Server: {settings.db_server}")
print(f"   Database: {settings.db_name}")
print(f"   Driver: {settings.db_driver}")

print(f"\n2. Database URL:")
print(f"   {settings.database_url[:100]}...")

print(f"\n3. Creating engine...")
try:
    engine = create_db_engine()
    print(f"   [OK] Engine created successfully")
except Exception as e:
    print(f"   [FAIL] Failed to create engine: {e}")
    sys.exit(1)

print(f"\n4. Testing connection...")
try:
    result = test_connection(engine)
    if result:
        print(f"   [OK] Connection test successful")
    else:
        print(f"   [FAIL] Connection test failed")
        sys.exit(1)
except Exception as e:
    print(f"   [FAIL] Connection test error: {e}")
    sys.exit(1)

print(f"\n5. Executing SQL Server version query...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION AS version"))
        row = result.fetchone()
        version = str(row[0])[:80]
        print(f"   [OK] {version}...")
except Exception as e:
    print(f"   [FAIL] Query failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
