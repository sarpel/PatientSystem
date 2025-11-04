"""
Database schema inspector for discovering and categorizing tables.
Uses SQLAlchemy Inspector to discover all tables and their metadata.
"""

from typing import Any, Dict, List

import yaml
from loguru import logger
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from src.database.connection import get_engine


class DatabaseInspector:
    """
    Inspects SQL Server database schema and categorizes tables.

    Categories based on table prefixes commonly used in AHBS (Aile Hekimliği Bilgi Sistemi):
    - GP_*: General Patient (Genel Hasta) - Main patient records
    - DTY_*: Detail (Detay) - Detail/sub-records
    - LST_*: List (Liste) - Reference/lookup tables
    - HRC_*: External (Harici) - External/supplementary data
    """

    # Table category definitions
    CATEGORIES = {
        "GP_": "Main Patient Records",
        "DTY_": "Detail Records",
        "LST_": "Reference Tables",
        "HRC_": "External Data",
        "OTHER": "Other Tables",
    }

    def __init__(self, engine: Engine = None):
        """
        Initialize database inspector.

        Args:
            engine: SQLAlchemy engine (uses default if not provided)
        """
        self.engine = engine or get_engine()
        self.inspector = inspect(self.engine)
        self.schema = None
        self._tables_cache = None

    def discover_all_tables(self, schema: str = None) -> List[str]:
        """
        Discover all tables in the database.

        Args:
            schema: Database schema name (uses default if not provided)

        Returns:
            List of table names
        """
        logger.info("Discovering all tables in database...")

        try:
            table_names = self.inspector.get_table_names(schema=schema)
            logger.info(f"Found {len(table_names)} tables")
            sorted_tables = sorted(table_names)
            self._tables_cache = sorted_tables
            self.schema = schema
            return sorted_tables
        except Exception as e:
            logger.error(f"Failed to discover tables: {e}")
            raise

    def get_all_table_names(self, schema: str = None) -> List[str]:
        """
        Get all table names in the database (alias for discover_all_tables).

        Args:
            schema: Database schema name (uses default if not provided)

        Returns:
            List of table names
        """
        return self.discover_all_tables(schema=schema)

    def get_database_name(self) -> str:
        """
        Get the database name from the engine.

        Returns:
            Database name
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DB_NAME()"))
                db_name = result.scalar()
                return db_name
        except Exception as e:
            logger.error(f"Failed to get database name: {e}")
            return "Unknown"

    def categorize_tables(self, tables: List[str] = None) -> Dict[str, List[str]]:
        """
        Categorize tables by their prefix.

        Args:
            tables: List of table names (uses cached if not provided)

        Returns:
            Dictionary mapping categories to table lists
        """
        if tables is None:
            if self._tables_cache is None:
                tables = self.discover_all_tables()
            else:
                tables = self._tables_cache

        categorized = {category: [] for category in self.CATEGORIES.keys()}

        for table in tables:
            categorized_flag = False
            for prefix in ["GP_", "DTY_", "LST_", "HRC_"]:
                if table.startswith(prefix):
                    categorized[prefix].append(table)
                    categorized_flag = True
                    break

            if not categorized_flag:
                categorized["OTHER"].append(table)

        # Log category statistics
        for category, description in self.CATEGORIES.items():
            count = len(categorized[category])
            logger.info(f"{description}: {count} tables")

        return categorized

    def get_table_schema(self, table_name: str, schema: str = None) -> Dict[str, Any]:
        """
        Get detailed schema information for a specific table.

        Args:
            table_name: Name of the table
            schema: Database schema name

        Returns:
            Dictionary mapping column names to column metadata (for CLI compatibility)
            or full table metadata (when called internally)
        """
        try:
            columns = self.inspector.get_columns(table_name, schema=schema)

            # Return simple column dict format for CLI compatibility
            return {
                col["name"]: {
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": col.get("default"),
                    "autoincrement": col.get("autoincrement", False),
                }
                for col in columns
            }
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            raise

    def get_table_schema_detailed(self, table_name: str, schema: str = None) -> Dict[str, Any]:
        """
        Get complete schema information including constraints and indexes.

        Args:
            table_name: Name of the table
            schema: Database schema name

        Returns:
            Dictionary containing complete table metadata
        """
        try:
            columns = self.inspector.get_columns(table_name, schema=schema)
            pk_constraint = self.inspector.get_pk_constraint(table_name, schema=schema)
            foreign_keys = self.inspector.get_foreign_keys(table_name, schema=schema)
            indexes = self.inspector.get_indexes(table_name, schema=schema)

            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": col.get("default"),
                        "autoincrement": col.get("autoincrement", False),
                    }
                    for col in columns
                ],
                "primary_key": pk_constraint.get("constrained_columns", []),
                "foreign_keys": [
                    {
                        "columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"],
                    }
                    for fk in foreign_keys
                ],
                "indexes": [
                    {"name": idx["name"], "columns": idx["column_names"], "unique": idx["unique"]}
                    for idx in indexes
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get detailed schema for table {table_name}: {e}")
            raise

    def get_table_row_count(self, table_name: str) -> int:
        """
        Get approximate row count for a table.

        Args:
            table_name: Name of the table

        Returns:
            Row count
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                return count
        except Exception as e:
            logger.warning(f"Failed to get row count for {table_name}: {e}")
            return 0

    def export_schema_yaml(self, output_path: str, include_details: bool = False) -> None:
        """
        Export database schema to YAML file.

        Args:
            output_path: Path to output YAML file
            include_details: Include detailed column information
        """
        logger.info(f"Exporting schema to {output_path}...")

        tables = self.discover_all_tables() if self._tables_cache is None else self._tables_cache
        categorized = self.categorize_tables(tables)

        schema_data = {
            "database_info": {
                "total_tables": len(tables),
                "schema": self.schema or "dbo",
                "categories": {
                    cat: {"description": desc, "count": len(categorized[cat])}
                    for cat, desc in self.CATEGORIES.items()
                },
            },
            "tables_by_category": {},
        }

        for category, table_list in categorized.items():
            schema_data["tables_by_category"][category] = {}

            for table in table_list:
                if include_details:
                    try:
                        schema_data["tables_by_category"][category][table] = (
                            self.get_table_schema_detailed(table)
                        )
                    except Exception as e:
                        logger.warning(f"Skipping detailed schema for {table}: {e}")
                        schema_data["tables_by_category"][category][table] = {
                            "table_name": table,
                            "error": str(e),
                        }
                else:
                    # Just list table names
                    schema_data["tables_by_category"][category][table] = {"table_name": table}

        # Write to YAML file
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(schema_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        logger.info(f"Schema exported successfully to {output_path}")

    def get_critical_tables_summary(self) -> Dict[str, Any]:
        """
        Get a summary of critical tables for the clinical system.

        Returns:
            Dictionary with critical table information
        """
        tables = self.discover_all_tables() if self._tables_cache is None else self._tables_cache
        categorized = self.categorize_tables(tables)

        # Define critical table patterns
        critical_patterns = {
            "Hasta Demografik": ["GP_HASTA_KAYIT", "GP_HASTA_OZLUK", "DTY_HASTA_OZLUK"],
            "Muayene & Vizit": ["GP_MUAYENE", "GP_HASTA_KABUL", "GP_HASTA_CIKIS"],
            "Tanı (ICD)": ["GP_MUAYENE", "DTY_MUAYENE_EK_TANI", "LST_ICD10"],
            "Reçete & İlaç": ["GP_RECETE", "DTY_RECETE_ILAC", "HRC_ILAC"],
            "Lab & Tetkik": ["GP_HASTANE_TETKIK_ISTEM", "DTY_HASTANE_ISTEM", "HRC_DTY_LAB_SONUC"],
            "Alerji": ["DTY_HASTA_OZLUK_ALERJI"],
            "Gebe İzlem": ["GP_GEBE_IZLEM", "DTY_GEBE_IZLEM"],
            "Bebek & Çocuk": ["GP_BC_IZLEM", "DTY_BC_IZLEM"],
            "Aşı": ["GP_ASI", "HRC_ASI_TAKVIMI"],
            "Kronik Hastalıklar": ["GP_DIYABET", "GP_KRONIK_HASTALIKLAR", "GP_HYP"],
        }

        summary = {
            "total_tables": len(tables),
            "categories": {cat: len(tables_list) for cat, tables_list in categorized.items()},
            "critical_tables": {},
        }

        for category, patterns in critical_patterns.items():
            found_tables = []
            for pattern in patterns:
                # Find tables that match the pattern (exact or substring)
                matching = [t for t in tables if pattern in t.upper()]
                found_tables.extend(matching)

            summary["critical_tables"][category] = {
                "patterns": patterns,
                "found": list(set(found_tables)),  # Remove duplicates
                "count": len(set(found_tables)),
            }

        return summary


def main():
    """CLI entry point for database inspection."""
    inspector = DatabaseInspector()

    print("=" * 60)
    print("DATABASE SCHEMA INSPECTION")
    print("=" * 60)

    # Discover all tables
    tables = inspector.discover_all_tables()
    print(f"\nTotal tables found: {len(tables)}")

    # Categorize tables
    categorized = inspector.categorize_tables()
    print("\nTable Categories:")
    for category, description in inspector.CATEGORIES.items():
        count = len(categorized[category])
        print(f"  {description}: {count} tables")

    # Get critical tables summary
    print("\nCritical Tables Summary:")
    summary = inspector.get_critical_tables_summary()
    for category, info in summary["critical_tables"].items():
        print(f"\n  {category}: {info['count']} tables found")
        for table in info["found"][:3]:  # Show first 3
            print(f"    - {table}")
        if len(info["found"]) > 3:
            print(f"    ... and {len(info['found']) - 3} more")

    # Export schema
    output_path = "config/database_schema.yaml"
    print(f"\nExporting schema to {output_path}...")
    inspector.export_schema_yaml(output_path, include_details=False)
    print("Export complete!")


if __name__ == "__main__":
    main()
