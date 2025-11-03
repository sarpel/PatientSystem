"""Database inspector dialog for viewing schema information."""

from typing import Any, Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from ...database.connection import get_engine
from ...database.inspector import DatabaseInspector


class DatabaseInspectorDialog(QDialog):
    """Dialog for inspecting database schema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Inspector")
        self.setMinimumSize(900, 600)

        self.engine = get_engine()
        self.inspector = DatabaseInspector(self.engine)

        self._setup_ui()
        self._load_tables()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Header
        db_name = self.inspector.get_database_name()
        header = QLabel(f"Database: {db_name}")
        header.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            background-color: #3b82f6;
            color: white;
            border-radius: 4px;
        """
        )
        layout.addWidget(header)

        # Main content - split view
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - table list
        left_widget = self._create_table_list_panel()
        splitter.addWidget(left_widget)

        # Right panel - schema details
        right_widget = self._create_schema_panel()
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_table_list_panel(self):
        """Create table list panel."""
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))

        self.category_combo = QComboBox()
        self.category_combo.addItems(
            [
                "All Tables",
                "Patient Tables",
                "Visit Tables",
                "Diagnosis Tables",
                "Prescription Tables",
                "Lab Tables",
                "Reference Tables",
            ]
        )
        self.category_combo.currentIndexChanged.connect(self._filter_tables)
        filter_layout.addWidget(self.category_combo)

        layout.addLayout(filter_layout)

        # Table list
        self.table_list = QTableWidget()
        self.table_list.setColumnCount(1)
        self.table_list.setHorizontalHeaderLabels(["Table Name"])
        self.table_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_list.setSelectionMode(QTableWidget.SingleSelection)
        self.table_list.cellClicked.connect(self._on_table_selected)

        layout.addWidget(self.table_list)

        # Count label
        self.count_label = QLabel("0 tables")
        self.count_label.setStyleSheet("padding: 4px; color: #6b7280;")
        layout.addWidget(self.count_label)

        return widget

    def _create_schema_panel(self):
        """Create schema details panel."""
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Selected table label
        self.selected_table_label = QLabel("Select a table to view schema")
        self.selected_table_label.setStyleSheet(
            """
            font-weight: bold;
            padding: 8px;
            background-color: #f3f4f6;
            border-radius: 4px;
        """
        )
        layout.addWidget(self.selected_table_label)

        # Schema table
        self.schema_table = QTableWidget()
        self.schema_table.setColumnCount(3)
        self.schema_table.setHorizontalHeaderLabels(["Column Name", "Type", "Nullable"])
        self.schema_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.schema_table)

        return widget

    def _load_tables(self):
        """Load all database tables."""
        self.all_tables = self.inspector.get_all_table_names()
        self._filter_tables()

    def _filter_tables(self):
        """Filter tables by category."""
        category = self.category_combo.currentText()

        if category == "All Tables":
            filtered_tables = self.all_tables
        else:
            # Categorize tables
            category_filters = {
                "Patient Tables": ["HASTA", "GP_BC"],
                "Visit Tables": ["MUAYENE", "KABUL"],
                "Diagnosis Tables": ["TANI", "ICD"],
                "Prescription Tables": ["RECETE", "ILAC"],
                "Lab Tables": ["TETKIK", "LAB"],
                "Reference Tables": ["LST_"],
            }

            filters = category_filters.get(category, [])
            filtered_tables = [t for t in self.all_tables if any(f in t for f in filters)]

        # Populate table list
        self.table_list.setRowCount(len(filtered_tables))

        for row, table_name in enumerate(sorted(filtered_tables)):
            self.table_list.setItem(row, 0, QTableWidgetItem(table_name))

        self.count_label.setText(f"{len(filtered_tables)} table(s)")

        # Clear schema view
        self.schema_table.setRowCount(0)
        self.selected_table_label.setText("Select a table to view schema")

    def _on_table_selected(self, row: int, column: int):
        """Handle table selection."""
        table_name = self.table_list.item(row, 0).text()
        self._display_schema(table_name)

    def _display_schema(self, table_name: str):
        """Display schema for selected table."""
        self.selected_table_label.setText(f"Table: {table_name}")

        schema = self.inspector.get_table_schema(table_name)

        if not schema:
            self.schema_table.setRowCount(0)
            return

        self.schema_table.setRowCount(len(schema))

        for row, (col_name, col_info) in enumerate(schema.items()):
            # Column name
            self.schema_table.setItem(row, 0, QTableWidgetItem(col_name))

            # Type
            col_type = str(col_info.get("type", "Unknown"))
            self.schema_table.setItem(row, 1, QTableWidgetItem(col_type))

            # Nullable
            nullable = "Yes" if col_info.get("nullable") else "No"
            nullable_item = QTableWidgetItem(nullable)

            if not col_info.get("nullable"):
                # Highlight required fields
                nullable_item.setForeground(Qt.GlobalColor.red)

            self.schema_table.setItem(row, 2, nullable_item)

        self.schema_table.resizeColumnsToContents()
