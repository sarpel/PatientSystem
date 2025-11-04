"""AI configuration dialog for model settings."""

import asyncio
from typing import Dict

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ...ai import create_ai_router
from ...config.settings import settings


class HealthCheckWorker(QThread):
    """Background worker for AI health checks."""

    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        """Run health checks in background."""
        try:
            router = create_ai_router()
            results = asyncio.run(router.health_check_all())
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class AIConfigDialog(QDialog):
    """Dialog for configuring AI provider settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Configuration")
        self.setMinimumSize(600, 500)
        self.worker = None
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Model selection group
        model_group = QGroupBox("Model Configuration")
        model_layout = QFormLayout(model_group)

        self.claude_combo = QComboBox()
        self.claude_combo.addItems(
            ["claude-sonnet-4.5", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        )
        model_layout.addRow("Claude Model:", self.claude_combo)

        self.openai_combo = QComboBox()
        self.openai_combo.addItems(["gpt-5", "gpt-5-mini", "gpt-4-turbo"])
        model_layout.addRow("OpenAI Model:", self.openai_combo)

        self.gemini_combo = QComboBox()
        self.gemini_combo.addItems(["gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"])
        model_layout.addRow("Gemini Model:", self.gemini_combo)

        self.ollama_combo = QComboBox()
        self.ollama_combo.addItems(["gemma:7b", "llama2:7b", "mistral:7b"])
        model_layout.addRow("Ollama Model:", self.ollama_combo)

        layout.addWidget(model_group)

        # Routing strategy group
        routing_group = QGroupBox("Routing Strategy")
        routing_layout = QFormLayout(routing_group)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["smart", "cost_optimized", "quality_first", "round_robin"])
        routing_layout.addRow("Strategy:", self.strategy_combo)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setSuffix(" seconds")
        routing_layout.addRow("Timeout:", self.timeout_spin)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(1)
        routing_layout.addRow("Temperature:", self.temperature_spin)

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setSingleStep(100)
        routing_layout.addRow("Max Tokens:", self.max_tokens_spin)

        layout.addWidget(routing_group)

        # Health status group
        status_group = QGroupBox("Provider Status")
        status_layout = QVBoxLayout(status_group)

        self.status_table = QTableWidget()
        self.status_table.setColumnCount(2)
        self.status_table.setHorizontalHeaderLabels(["Provider", "Status"])
        self.status_table.setRowCount(4)
        self.status_table.setEditTriggers(QTableWidget.NoEditTriggers)

        providers = ["Ollama", "Claude", "OpenAI", "Gemini"]
        for row, provider in enumerate(providers):
            self.status_table.setItem(row, 0, QTableWidgetItem(provider))
            self.status_table.setItem(row, 1, QTableWidgetItem("Unknown"))

        status_layout.addWidget(self.status_table)

        # Health check button
        check_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        check_layout.addWidget(self.progress_bar)

        self.check_button = QPushButton("Check Provider Health")
        self.check_button.clicked.connect(self._check_health)
        check_layout.addWidget(self.check_button)

        status_layout.addLayout(check_layout)
        layout.addWidget(status_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_settings(self):
        """Load current settings from config."""
        self.claude_combo.setCurrentText(settings.claude_model)
        self.openai_combo.setCurrentText(settings.openai_model)
        self.gemini_combo.setCurrentText(settings.gemini_model)
        self.ollama_combo.setCurrentText(settings.ollama_model)
        self.strategy_combo.setCurrentText(settings.ai_routing_strategy)
        self.timeout_spin.setValue(settings.ai_timeout)
        self.temperature_spin.setValue(settings.ai_temperature)
        self.max_tokens_spin.setValue(settings.ai_max_tokens)

    def _save_settings(self):
        """Save settings (would update .env or config file)."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings saved. Please restart the application for changes to take effect.\n\n"
            "Note: API keys must be configured in the .env file.",
        )
        self.accept()

    def _check_health(self):
        """Run health checks on all AI providers."""
        self.progress_bar.setVisible(True)
        self.check_button.setEnabled(False)

        # Clear current status
        for row in range(self.status_table.rowCount()):
            self.status_table.setItem(row, 1, QTableWidgetItem("Checking..."))

        # Start worker
        self.worker = HealthCheckWorker()
        self.worker.finished.connect(self._on_health_check_complete)
        self.worker.error.connect(self._on_health_check_error)
        self.worker.start()

    def _on_health_check_complete(self, results: Dict[str, bool]):
        """Handle health check completion."""
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)

        provider_map = {"ollama": 0, "claude": 1, "openai": 2, "gemini": 3}

        for provider, status in results.items():
            row = provider_map.get(provider.lower())
            if row is not None:
                status_text = "✓ Available" if status else "✗ Unavailable"
                color = "green" if status else "red"

                item = QTableWidgetItem(status_text)
                item.setForeground(Qt.GlobalColor.green if status else Qt.GlobalColor.red)
                self.status_table.setItem(row, 1, item)

    def _on_health_check_error(self, error_msg: str):
        """Handle health check error."""
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)

        QMessageBox.critical(
            self, "Health Check Error", f"Failed to check provider health:\n{error_msg}"
        )
