"""Patient search widget with TCKN and name search."""

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...database.connection import get_session
from ...models.patient import Patient


class PatientSearchWidget(QWidget):
    """Widget for searching patients by TCKN or name."""

    patient_selected = Signal(str)  # Emits TCKN when patient selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search input row
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter TCKN or patient name...")
        self.search_input.returnPressed.connect(self._perform_search)
        search_layout.addWidget(self.search_input, stretch=1)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(
            ["TCKN", "Full Name", "Birth Date", "Gender", "Last Visit"]
        )
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setMaximumHeight(200)
        self.results_table.cellDoubleClicked.connect(self._on_row_selected)

        layout.addWidget(self.results_table)

        # Results count label
        self.results_label = QLabel("Enter search criteria")
        self.results_label.setStyleSheet("color: #6b7280; padding: 4px;")
        layout.addWidget(self.results_label)

    def _perform_search(self):
        """Execute patient search."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Search", "Please enter search criteria")
            return

        if len(query) < 2:
            QMessageBox.warning(self, "Search", "Please enter at least 2 characters")
            return

        try:
            with get_session() as session:
                # Search by TCKN or name
                patients_query = session.query(Patient)

                if query.isdigit():
                    # Search by TCKN (HASTA_KIMLIK_NO)
                    patients = (
                        patients_query.filter(Patient.HASTA_KIMLIK_NO.like(f"{query}%"))
                        .limit(20)
                        .all()
                    )
                else:
                    # Search by name
                    patients = (
                        patients_query.filter(
                            (Patient.AD.ilike(f"%{query}%")) | (Patient.SOYAD.ilike(f"%{query}%"))
                        )
                        .limit(20)
                        .all()
                    )

                self._display_results(patients)

        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Failed to search patients:\n{str(e)}")

    def _display_results(self, patients: List[Patient]):
        """Display search results in table."""
        self.results_table.setRowCount(len(patients))

        for row, patient in enumerate(patients):
            # TCKN (HASTA_KIMLIK_NO)
            tckn = str(patient.HASTA_KIMLIK_NO) if patient.HASTA_KIMLIK_NO else ""
            self.results_table.setItem(row, 0, QTableWidgetItem(tckn))

            # Full name
            full_name = f"{patient.AD or ''} {patient.SOYAD or ''}".strip()
            self.results_table.setItem(row, 1, QTableWidgetItem(full_name))

            # Birth date
            birth_date = patient.DOGUM_TARIHI.strftime("%Y-%m-%d") if patient.DOGUM_TARIHI else ""
            self.results_table.setItem(row, 2, QTableWidgetItem(birth_date))

            # Gender
            gender_map = {1: "Male", 2: "Female"}
            gender = gender_map.get(
                patient.CINSIYET, str(patient.CINSIYET) if patient.CINSIYET else ""
            )
            self.results_table.setItem(row, 3, QTableWidgetItem(gender))

            # Last visit (placeholder - would need join with Visit table)
            self.results_table.setItem(row, 4, QTableWidgetItem("-"))

        # Update results label
        self.results_label.setText(f"Found {len(patients)} patient(s)")

        # Resize columns to content
        self.results_table.resizeColumnsToContents()

    def _on_row_selected(self, row: int, column: int):
        """Handle row selection."""
        tckn_item = self.results_table.item(row, 0)
        if tckn_item:
            tckn = tckn_item.text()
            if tckn:
                self.patient_selected.emit(tckn)
