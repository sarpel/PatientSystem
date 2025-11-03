"""
Unit tests for database inspector module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import yaml

from src.database.inspector import DatabaseInspector


class TestDatabaseInspector:
    """Test suite for DatabaseInspector class."""

    @pytest.fixture
    def mock_engine(self):
        """Create a mock SQLAlchemy engine."""
        engine = Mock()
        return engine

    @pytest.fixture
    def mock_inspector(self):
        """Create a mock SQLAlchemy Inspector."""
        inspector = Mock()
        return inspector

    @pytest.fixture
    def sample_tables(self):
        """Sample table names for testing."""
        return [
            'GP_HASTA_KAYIT',
            'GP_MUAYENE',
            'DTY_HASTA_OZLUK_ALERJI',
            'DTY_MUAYENE_EK_TANI',
            'LST_ICD10',
            'LST_ILCE',
            'HRC_ILAC',
            'HRC_ASI_TAKVIMI',
            'SYSTEM_LOG',
            'CONFIG_SETTINGS'
        ]

    @pytest.fixture
    def db_inspector(self, mock_engine, mock_inspector):
        """Create DatabaseInspector instance with mocked dependencies."""
        with patch('src.database.inspector.get_engine', return_value=mock_engine), \
             patch('src.database.inspector.inspect', return_value=mock_inspector):
            inspector = DatabaseInspector()
            inspector.inspector = mock_inspector
            return inspector

    def test_initialization(self, mock_engine):
        """Test DatabaseInspector initialization."""
        with patch('src.database.inspector.get_engine', return_value=mock_engine), \
             patch('src.database.inspector.inspect') as mock_inspect:
            inspector = DatabaseInspector()

            assert inspector.engine == mock_engine
            mock_inspect.assert_called_once_with(mock_engine)
            assert inspector.schema is None
            assert inspector._tables_cache is None

    def test_discover_all_tables(self, db_inspector, sample_tables):
        """Test discovering all tables in database."""
        db_inspector.inspector.get_table_names.return_value = sample_tables

        result = db_inspector.discover_all_tables()

        assert len(result) == len(sample_tables)
        # Result should be sorted alphabetically
        assert result == sorted(result)
        # Cache should contain the same result
        assert db_inspector._tables_cache == result
        # All tables from sample should be in result
        assert set(result) == set(sample_tables)
        db_inspector.inspector.get_table_names.assert_called_once_with(schema=None)

    def test_discover_all_tables_with_schema(self, db_inspector, sample_tables):
        """Test discovering tables with specific schema."""
        db_inspector.inspector.get_table_names.return_value = sample_tables

        result = db_inspector.discover_all_tables(schema='dbo')

        assert db_inspector.schema == 'dbo'
        db_inspector.inspector.get_table_names.assert_called_once_with(schema='dbo')

    def test_categorize_tables(self, db_inspector, sample_tables):
        """Test table categorization by prefix."""
        db_inspector._tables_cache = sample_tables

        result = db_inspector.categorize_tables()

        assert 'GP_' in result
        assert 'DTY_' in result
        assert 'LST_' in result
        assert 'HRC_' in result
        assert 'OTHER' in result

        assert len(result['GP_']) == 2  # GP_HASTA_KAYIT, GP_MUAYENE
        assert len(result['DTY_']) == 2  # DTY_HASTA_OZLUK_ALERJI, DTY_MUAYENE_EK_TANI
        assert len(result['LST_']) == 2  # LST_ICD10, LST_ILCE
        assert len(result['HRC_']) == 2  # HRC_ILAC, HRC_ASI_TAKVIMI
        assert len(result['OTHER']) == 2  # SYSTEM_LOG, CONFIG_SETTINGS

    def test_categorize_tables_with_provided_list(self, db_inspector):
        """Test categorization with explicitly provided table list."""
        tables = ['GP_TEST', 'DTY_TEST', 'UNCATEGORIZED']

        result = db_inspector.categorize_tables(tables)

        assert len(result['GP_']) == 1
        assert len(result['DTY_']) == 1
        assert len(result['OTHER']) == 1
        assert 'GP_TEST' in result['GP_']
        assert 'DTY_TEST' in result['DTY_']
        assert 'UNCATEGORIZED' in result['OTHER']

    def test_get_table_schema(self, db_inspector):
        """Test getting detailed schema for a table."""
        # Mock column data
        mock_columns = [
            {
                'name': 'id',
                'type': Mock(__str__=lambda self: 'INTEGER'),
                'nullable': False,
                'default': None,
                'autoincrement': True
            },
            {
                'name': 'name',
                'type': Mock(__str__=lambda self: 'VARCHAR(100)'),
                'nullable': True,
                'default': None
            }
        ]

        # Mock constraints and indexes
        mock_pk = {'constrained_columns': ['id']}
        mock_fks = [
            {
                'constrained_columns': ['user_id'],
                'referred_table': 'users',
                'referred_columns': ['id']
            }
        ]
        mock_indexes = [
            {
                'name': 'idx_name',
                'column_names': ['name'],
                'unique': False
            }
        ]

        db_inspector.inspector.get_columns.return_value = mock_columns
        db_inspector.inspector.get_pk_constraint.return_value = mock_pk
        db_inspector.inspector.get_foreign_keys.return_value = mock_fks
        db_inspector.inspector.get_indexes.return_value = mock_indexes

        result = db_inspector.get_table_schema('test_table')

        assert result['table_name'] == 'test_table'
        assert len(result['columns']) == 2
        assert result['columns'][0]['name'] == 'id'
        assert result['columns'][0]['type'] == 'INTEGER'
        assert result['primary_key'] == ['id']
        assert len(result['foreign_keys']) == 1
        assert len(result['indexes']) == 1

    def test_get_table_row_count(self, db_inspector, mock_engine):
        """Test getting row count for a table."""
        mock_result = Mock()
        mock_result.scalar.return_value = 42

        mock_connection = MagicMock()
        mock_connection.execute.return_value = mock_result

        # Properly mock the context manager
        mock_context = MagicMock()
        mock_context.__enter__ = Mock(return_value=mock_connection)
        mock_context.__exit__ = Mock(return_value=False)
        mock_engine.connect.return_value = mock_context

        count = db_inspector.get_table_row_count('test_table')

        assert count == 42

    def test_get_table_row_count_error(self, db_inspector, mock_engine):
        """Test row count with database error."""
        mock_engine.connect.side_effect = Exception("Connection failed")

        count = db_inspector.get_table_row_count('test_table')

        assert count == 0

    def test_export_schema_yaml_basic(self, db_inspector, sample_tables):
        """Test exporting schema to YAML without details."""
        db_inspector._tables_cache = sample_tables
        db_inspector.inspector.get_table_names.return_value = sample_tables

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            temp_path = f.name

        try:
            db_inspector.export_schema_yaml(temp_path, include_details=False)

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify YAML content
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            assert 'database_info' in data
            assert 'tables_by_category' in data
            assert data['database_info']['total_tables'] == len(sample_tables)
            assert 'categories' in data['database_info']

            # Verify categories
            for category in ['GP_', 'DTY_', 'LST_', 'HRC_', 'OTHER']:
                assert category in data['tables_by_category']

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_export_schema_yaml_with_details(self, db_inspector, sample_tables):
        """Test exporting schema with detailed table information."""
        db_inspector._tables_cache = sample_tables[:2]  # Use smaller set for detailed export
        db_inspector.inspector.get_table_names.return_value = sample_tables[:2]

        # Mock get_table_schema
        mock_schema = {
            'table_name': 'GP_HASTA_KAYIT',
            'columns': [{'name': 'id', 'type': 'INTEGER'}],
            'primary_key': ['id'],
            'foreign_keys': [],
            'indexes': []
        }
        db_inspector.get_table_schema = Mock(return_value=mock_schema)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            temp_path = f.name

        try:
            db_inspector.export_schema_yaml(temp_path, include_details=True)

            with open(temp_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Verify detailed schema is included
            gp_tables = data['tables_by_category']['GP_']
            assert 'GP_HASTA_KAYIT' in gp_tables
            table_data = gp_tables['GP_HASTA_KAYIT']
            assert 'columns' in table_data
            assert 'primary_key' in table_data

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_get_critical_tables_summary(self, db_inspector):
        """Test getting summary of critical tables."""
        critical_tables = [
            'GP_HASTA_KAYIT',
            'GP_HASTA_OZLUK',
            'GP_MUAYENE',
            'GP_HASTA_KABUL',
            'DTY_MUAYENE_EK_TANI',
            'LST_ICD10',
            'HRC_ILAC'
        ]
        db_inspector._tables_cache = critical_tables

        summary = db_inspector.get_critical_tables_summary()

        assert 'total_tables' in summary
        assert 'categories' in summary
        assert 'critical_tables' in summary

        # Check specific critical categories
        assert 'Hasta Demografik' in summary['critical_tables']
        assert 'Muayene & Vizit' in summary['critical_tables']

        # Verify GP_MUAYENE is found in multiple categories
        muayene_vizit = summary['critical_tables']['Muayene & Vizit']
        assert 'GP_MUAYENE' in muayene_vizit['found']
        assert muayene_vizit['count'] > 0

    def test_category_constants(self):
        """Test that category constants are properly defined."""
        assert 'GP_' in DatabaseInspector.CATEGORIES
        assert 'DTY_' in DatabaseInspector.CATEGORIES
        assert 'LST_' in DatabaseInspector.CATEGORIES
        assert 'HRC_' in DatabaseInspector.CATEGORIES
        assert 'OTHER' in DatabaseInspector.CATEGORIES

        # Verify descriptions are in English (not Turkish - avoid encoding issues)
        assert 'Main Patient' in DatabaseInspector.CATEGORIES['GP_']
        assert 'Detail' in DatabaseInspector.CATEGORIES['DTY_']
        assert 'Reference' in DatabaseInspector.CATEGORIES['LST_']
        assert 'External' in DatabaseInspector.CATEGORIES['HRC_']
