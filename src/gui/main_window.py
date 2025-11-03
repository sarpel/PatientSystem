"""Main window for Clinical AI Assistant Desktop Application."""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QStatusBar, QLabel, QMessageBox,
    QTabWidget, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QIcon, QFont

from ..database.connection import get_engine, get_session
from .widgets.patient_search import PatientSearchWidget
from .widgets.clinical_dashboard import ClinicalDashboardWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinical AI Assistant")
        self.setMinimumSize(1200, 800)

        # Load stylesheet
        self._load_styles()

        # Create menu bar
        self._create_menus()

        # Create central widget
        self._create_central_widget()

        # Create status bar
        self._create_status_bar()

        # Start database connection check
        self._check_database_connection()

    def _load_styles(self):
        """Load Qt stylesheet for medical theme."""
        style_path = Path(__file__).parent / "resources" / "styles.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            # Fallback inline style
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f7fa;
                }
                QTabWidget::pane {
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #e5e7eb;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #3b82f6;
                    color: white;
                }
                QStatusBar {
                    background-color: #374151;
                    color: white;
                }
            """)

    def _create_menus(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        db_inspector_action = QAction("Database &Inspector", self)
        db_inspector_action.triggered.connect(self._show_database_inspector)
        tools_menu.addAction(db_inspector_action)

        ai_config_action = QAction("AI &Configuration", self)
        ai_config_action.triggered.connect(self._show_ai_config)
        tools_menu.addAction(ai_config_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create main central widget with patient search and dashboard."""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Patient search widget
        self.patient_search = PatientSearchWidget()
        layout.addWidget(self.patient_search)

        # Clinical dashboard
        self.dashboard = ClinicalDashboardWidget()
        layout.addWidget(self.dashboard, stretch=1)

        # Connect signals
        self.patient_search.patient_selected.connect(self.dashboard.load_patient)

        self.setCentralWidget(central_widget)

    def _create_status_bar(self):
        """Create status bar with database connection indicator."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Database connection status
        self.db_status_label = QLabel("Database: Checking...")
        self.db_status_label.setStyleSheet("padding: 2px 10px;")
        status_bar.addPermanentWidget(self.db_status_label)

        # AI provider status
        self.ai_status_label = QLabel("AI: Ready")
        self.ai_status_label.setStyleSheet("padding: 2px 10px;")
        status_bar.addPermanentWidget(self.ai_status_label)

    def _check_database_connection(self):
        """Check database connectivity and update status."""
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            self.db_status_label.setText("Database: Connected ✓")
            self.db_status_label.setStyleSheet(
                "padding: 2px 10px; color: #10b981; font-weight: bold;"
            )
        except Exception as e:
            self.db_status_label.setText("Database: Disconnected ✗")
            self.db_status_label.setStyleSheet(
                "padding: 2px 10px; color: #ef4444; font-weight: bold;"
            )
            QMessageBox.warning(
                self,
                "Database Connection Error",
                f"Failed to connect to database:\n{str(e)}\n\n"
                "Please check your database configuration."
            )

    def _show_database_inspector(self):
        """Show database inspector dialog."""
        from .dialogs.database_inspector_dialog import DatabaseInspectorDialog
        dialog = DatabaseInspectorDialog(self)
        dialog.exec()

    def _show_ai_config(self):
        """Show AI configuration dialog."""
        from .dialogs.ai_config_dialog import AIConfigDialog
        dialog = AIConfigDialog(self)
        dialog.exec()

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Clinical AI Assistant",
            "<h2>Clinical AI Assistant</h2>"
            "<p>Version 0.1.0</p>"
            "<p>AI-powered clinical decision support system</p>"
            "<p>Built with PySide6, SQLAlchemy, and modern AI models</p>"
        )


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Clinical AI Assistant")
    app.setOrganizationName("Clinical AI")
    app.setApplicationVersion("0.1.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
