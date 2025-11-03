"""Drug interaction alert dialog with severity-based styling."""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DrugInteractionAlertDialog(QDialog):
    """Dialog for displaying drug interaction alerts."""

    def __init__(self, interactions: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.interactions = interactions
        self.setWindowTitle("⚠️ Drug Interaction Alert")
        self.setMinimumSize(700, 500)
        self._setup_ui()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Header with warning
        header = QLabel("🚨 DRUG INTERACTIONS DETECTED")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #dc2626; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Count label
        count_label = QLabel(f"Found {len(self.interactions)} interaction(s)")
        count_label.setStyleSheet("padding: 5px; color: #6b7280;")
        layout.addWidget(count_label)

        # Interactions table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Type", "Severity", "Drugs", "Effect"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self._populate_table()
        layout.addWidget(self.table)

        # Alternative medications
        if self._has_alternatives():
            alt_label = QLabel("💊 Alternative Medications:")
            alt_label.setStyleSheet("font-weight: bold; padding: 5px;")
            layout.addWidget(alt_label)

            self.alternatives_text = QTextEdit()
            self.alternatives_text.setReadOnly(True)
            self.alternatives_text.setMaximumHeight(80)
            self._populate_alternatives()
            layout.addWidget(self.alternatives_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

    def _populate_table(self):
        """Populate interactions table."""
        self.table.setRowCount(len(self.interactions))

        severity_colors = {
            "critical": ("#7f1d1d", "#fee2e2"),  # dark red text, light red bg
            "major": ("#991b1b", "#fef2f2"),     # red text, very light red bg
            "moderate": ("#92400e", "#fef3c7"),   # amber text, light amber bg
            "minor": ("#065f46", "#d1fae5"),     # green text, light green bg
        }

        for row, interaction in enumerate(self.interactions):
            # Type
            type_item = QTableWidgetItem(interaction.get("type", ""))
            self.table.setItem(row, 0, type_item)

            # Severity with color coding
            severity = interaction.get("severity", "moderate")
            severity_item = QTableWidgetItem(severity.upper())

            if severity in severity_colors:
                text_color, bg_color = severity_colors[severity]
                severity_item.setForeground(Qt.GlobalColor(text_color))
                severity_item.setBackground(Qt.GlobalColor(bg_color))

            severity_font = QFont()
            severity_font.setBold(True)
            severity_item.setFont(severity_font)

            self.table.setItem(row, 1, severity_item)

            # Drugs
            drug1 = interaction.get("drug1", "")
            drug2 = interaction.get("drug2", "")
            drugs_item = QTableWidgetItem(f"{drug1} + {drug2}")
            self.table.setItem(row, 2, drugs_item)

            # Effect
            effect_item = QTableWidgetItem(interaction.get("effect", ""))
            self.table.setItem(row, 3, effect_item)

        self.table.resizeColumnsToContents()

    def _has_alternatives(self) -> bool:
        """Check if any interaction has alternatives."""
        return any(
            interaction.get("alternative_drugs")
            for interaction in self.interactions
        )

    def _populate_alternatives(self):
        """Populate alternatives text."""
        alternatives = []
        for interaction in self.interactions:
            alt_list = interaction.get("alternative_drugs", [])
            if alt_list:
                drug1 = interaction.get("drug1", "Unknown")
                alternatives.append(f"Instead of {drug1}:")
                for alt in alt_list:
                    alternatives.append(f"  • {alt}")

        self.alternatives_text.setPlainText("\n".join(alternatives))
