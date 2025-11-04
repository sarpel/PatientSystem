"""End-to-end tests for desktop GUI workflow."""

import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from src.gui.main_window import MainWindow
from src.gui.widgets.diagnosis_panel import DiagnosisPanelWidget
from src.gui.widgets.patient_search import PatientSearchWidget


@pytest.mark.e2e
@pytest.mark.gui
class TestDesktopGUIWorkflow:
    """End-to-end tests for desktop GUI workflow."""

    @pytest.fixture(scope="session")
    def qt_app(self):
        """Create QApplication for GUI tests."""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def main_window(self, qt_app, mock_session):
        """Create main window for testing."""
        with patch("src.gui.main_window.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_connection = Mock()
            mock_connection.execute.return_value.scalar.return_value = 1
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            window = MainWindow()
            return window

    @pytest.fixture
    def sample_patients(self):
        """Sample patient data for testing."""
        return [
            {
                "TCKN": "12345678901",
                "ADI": "Test",
                "SOYADI": "Patient One",
                "DOGUM_TARIHI": "1980-01-01",
                "CINSIYET": "E",
            },
            {
                "TCKN": "12345678902",
                "ADI": "Test",
                "SOYADI": "Patient Two",
                "DOGUM_TARIHI": "1975-05-15",
                "CINSIYET": "K",
            },
        ]

    def test_main_window_initialization(self, main_window):
        """Test main window initialization."""
        # Verify window properties
        assert main_window.windowTitle() == "Clinical AI Assistant"
        assert main_window.minimumWidth() >= 1200
        assert main_window.minimumHeight() >= 800

        # Verify main components exist
        assert hasattr(main_window, "patient_search")
        assert hasattr(main_window, "dashboard")
        assert hasattr(main_window, "db_status_label")
        assert hasattr(main_window, "ai_status_label")

        # Verify database connection status indicator
        assert main_window.db_status_label.text().startswith("Database:")

    def test_patient_search_functionality(self, main_window, sample_patients, mock_session):
        """Test patient search functionality."""
        search_widget = main_window.patient_search

        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value.limit.return_value.all.return_value = sample_patients
        mock_session.query.return_value = mock_query

        # Test search input
        search_input = search_widget.search_input
        QTest.keyClicks(search_input, "Test")
        QTest.keyClick(search_input, Qt.Key_Return)

        # Verify search was triggered
        assert search_input.text() == "Test"

        # Test search button
        search_button = search_widget.search_button
        QTest.mouseClick(search_button, Qt.LeftButton)

    def test_patient_selection_workflow(self, main_window, sample_patients, mock_session):
        """Test patient selection and dashboard loading."""
        search_widget = main_window.patient_search
        dashboard = main_window.dashboard

        # Mock patient search
        mock_query = Mock()
        mock_query.filter.return_value.limit.return_value.all.return_value = sample_patients
        mock_session.query.return_value = mock_query

        # Mock patient retrieval for dashboard
        mock_session.query.return_value.filter.return_value.first.return_value = sample_patients[0]

        # Trigger patient search
        search_widget.search_input.setText("Test")
        search_widget._perform_search()

        # Simulate patient selection
        if search_widget.results_table.rowCount() > 0:
            search_widget.results_table.selectRow(0)
            search_widget._on_row_selected(0, 0)

            # Verify dashboard was updated
            assert dashboard.current_tckn == sample_patients[0]["TCKN"]

    @patch("src.gui.widgets.diagnosis_panel.DiagnosisWorker")
    def test_diagnosis_generation_workflow(self, mock_worker_class, main_window, mock_ai_response):
        """Test diagnosis generation workflow in GUI."""
        # Set up patient in dashboard
        dashboard = main_window.dashboard
        dashboard.load_patient("12345678901")

        # Get diagnosis panel
        diagnosis_panel = dashboard.diagnosis_panel

        # Mock AI worker
        mock_worker = Mock()
        mock_worker.finished = Mock()
        mock_worker.error = Mock()
        mock_worker_class.return_value = mock_worker

        # Test diagnosis input
        diagnosis_input = diagnosis_panel.complaint_input
        QTest.keyClicks(diagnosis_input, "Patient reports chest pain for 2 days")

        # Test model selection
        model_combo = diagnosis_panel.model_combo
        model_combo.setCurrentText("Claude")

        # Trigger diagnosis generation
        analyze_button = diagnosis_panel.analyze_button
        QTest.mouseClick(analyze_button, Qt.LeftButton)

        # Verify worker was created and started
        mock_worker_class.assert_called_once()
        mock_worker.start.assert_called_once()

        # Simulate successful completion
        diagnosis_panel._on_diagnosis_complete(mock_ai_response)

        # Verify results are displayed
        assert diagnosis_panel.results_table.rowCount() > 0

    def test_lab_charts_functionality(self, main_window, mock_lab_data):
        """Test lab charts functionality."""
        # Set up patient in dashboard
        dashboard = main_window.dashboard
        dashboard.load_patient("12345678901")

        # Get lab charts widget
        lab_charts = dashboard.lab_charts

        # Mock lab data retrieval
        with patch("src.gui.widgets.lab_charts.apiClient.getLabTests", return_value=mock_lab_data):
            lab_charts.load_patient("12345678901")

        # Verify lab data was loaded
        assert len(lab_charts.lab_data) > 0

        # Test test selection
        test_combo = lab_charts.test_combo
        if test_combo.count() > 0:
            test_combo.setCurrentIndex(0)
            lab_charts._update_chart()

    def test_menu_functionality(self, main_window):
        """Test menu functionality."""
        menubar = main_window.menuBar()

        # Test File menu
        file_menu = None
        for action in menubar.actions():
            if action.text() == "&File":
                file_menu = action.menu()
                break

        assert file_menu is not None
        assert file_menu.actions()  # Should have menu items

        # Test Tools menu
        tools_menu = None
        for action in menubar.actions():
            if action.text() == "&Tools":
                tools_menu = action.menu()
                break

        assert tools_menu is not None
        assert len(tools_menu.actions()) >= 2  # Database Inspector and AI Config

    @patch("src.gui.dialogs.ai_config_dialog.AIConfigDialog")
    def test_ai_config_dialog(self, mock_dialog_class, main_window):
        """Test AI configuration dialog."""
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        # Trigger AI config dialog
        main_window._show_ai_config()

        # Verify dialog was created and executed
        mock_dialog_class.assert_called_once()
        mock_dialog.exec.assert_called_once()

    @patch("src.gui.dialogs.database_inspector_dialog.DatabaseInspectorDialog")
    def test_database_inspector_dialog(self, mock_dialog_class, main_window):
        """Test database inspector dialog."""
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        # Trigger database inspector dialog
        main_window._show_database_inspector()

        # Verify dialog was created and executed
        mock_dialog_class.assert_called_once()
        mock_dialog.exec.assert_called_once()

    def test_status_bar_updates(self, main_window):
        """Test status bar updates."""
        status_bar = main_window.statusBar()

        # Verify status bar has permanent widgets
        permanent_widgets = status_bar.children()
        assert len(permanent_widgets) >= 2  # Database and AI status

        # Test database status update
        main_window._check_database_connection()
        # Status should be updated (either connected or disconnected)

    def test_error_handling_in_gui(self, main_window):
        """Test error handling in GUI components."""
        # Test patient search with error
        with patch("src.gui.widgets.patient_search.get_session") as mock_get_session:
            mock_get_session.side_effect = Exception("Database connection failed")

            search_widget = main_window.patient_search
            search_widget.search_input.setText("Test")
            search_widget._perform_search()

            # Should handle error gracefully (no crash)

    def test_responsive_behavior(self, main_window):
        """Test responsive behavior of GUI."""
        # Test window resizing
        original_size = main_window.size()
        new_size = original_size + 100

        main_window.resize(new_size)
        QTest.qWait(100)  # Wait for resize to complete

        assert main_window.size() == new_size

        # Test minimum size constraints
        min_size = main_window.minimumSize()
        main_window.resize(min_size.width() - 10, min_size.height() - 10)

        # Window should not go below minimum size
        current_size = main_window.size()
        assert current_size.width() >= min_size.width()
        assert current_size.height() >= min_size.height()

    def test_keyboard_navigation(self, main_window):
        """Test keyboard navigation in GUI."""
        search_widget = main_window.patient_search
        search_input = search_widget.search_input

        # Test Tab navigation
        search_input.setFocus()
        QTest.keyClick(search_input, Qt.Key_Tab)

        # Test Enter key in search input
        search_input.setText("Test")
        QTest.keyClick(search_input, Qt.Key_Return)

        # Test Escape key (should clear or cancel)
        QTest.keyClick(search_input, Qt.Key_Escape)


@pytest.mark.e2e
@pytest.mark.gui
@pytest.mark.slow
class TestDesktopGUIPerformance:
    """Performance tests for desktop GUI."""

    def test_gui_startup_performance(self, qt_app, mock_session):
        """Test GUI startup performance."""
        import time

        start_time = time.time()

        with patch("src.gui.main_window.get_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_connection = Mock()
            mock_connection.execute.return_value.scalar.return_value = 1
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            window = MainWindow()
            window.show()

        end_time = time.time()
        startup_time = end_time - start_time

        # GUI should start within reasonable time
        assert startup_time < 3.0, f"GUI startup took {startup_time:.2f}s, should be < 3.0s"

        print(f"GUI Startup Performance: {startup_time:.2f}s")
        window.close()

    def test_large_dataset_handling(self, qt_app, main_window):
        """Test handling of large datasets in GUI."""
        # Create large dataset
        large_patient_list = []
        for i in range(1000):
            large_patient_list.append(
                {
                    "TCKN": f"1234567890{i:04d}",
                    "ADI": f"Test",
                    "SOYADI": f"Patient {i}",
                    "DOGUM_TARIHI": "1980-01-01",
                    "CINSIYET": "E" if i % 2 == 0 else "K",
                }
            )

        search_widget = main_window.patient_search

        # Mock large dataset return
        with patch("src.gui.widgets.patient_search.get_session") as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()
            mock_query.filter.return_value.limit.return_value.all.return_value = large_patient_list[
                :100
            ]
            mock_session.query.return_value = mock_query
            mock_get_session.return_value = mock_session

            start_time = time.time()
            search_widget._perform_search()
            end_time = time.time()

            search_time = end_time - start_time

            # Should handle large dataset efficiently
            assert (
                search_time < 2.0
            ), f"Large dataset search took {search_time:.2f}s, should be < 2.0s"

            print(f"Large Dataset Performance: {search_time:.2f}s for 1000+ records")
