"""Settings dialog: OCR engine, hotkey, and AWS options."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import Settings


class SettingsDialog(QDialog):
    """Edits a copy of Settings; returns the updated object on accept."""

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self._settings = settings

        form = QFormLayout()

        self.engine = QComboBox()
        self.engine.addItem("Tesseract (offline)", "tesseract")
        self.engine.addItem("AWS (cloud)", "aws")
        self.engine.setCurrentIndex(0 if settings.ocr_engine == "tesseract" else 1)
        form.addRow("OCR engine", self.engine)

        self.hotkey = QLineEdit(settings.hotkey)
        self.hotkey.setPlaceholderText("<ctrl>+<shift>+x")
        form.addRow("Global hotkey", self.hotkey)

        self.tess_lang = QLineEdit(settings.tesseract_lang)
        form.addRow("Tesseract language", self.tess_lang)

        self.tess_cmd = QLineEdit(settings.tesseract_cmd)
        self.tess_cmd.setPlaceholderText("Auto-detected if left blank")
        form.addRow("Tesseract path", self.tess_cmd)

        self.aws_backend = QComboBox()
        self.aws_backend.addItem("Textract", "textract")
        self.aws_backend.addItem("Bedrock", "bedrock")
        self.aws_backend.setCurrentIndex(
            0 if settings.aws_backend == "textract" else 1
        )
        form.addRow("AWS backend", self.aws_backend)

        self.aws_region = QLineEdit(settings.aws_region)
        form.addRow("AWS region", self.aws_region)

        layout = QVBoxLayout(self)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def result_settings(self) -> Settings:
        """Return the settings updated with the dialog's current values."""
        self._settings.ocr_engine = self.engine.currentData()
        self._settings.hotkey = self.hotkey.text().strip() or self._settings.hotkey
        self._settings.tesseract_lang = self.tess_lang.text().strip() or "eng"
        self._settings.tesseract_cmd = self.tess_cmd.text().strip()
        self._settings.aws_backend = self.aws_backend.currentData()
        self._settings.aws_region = self.aws_region.text().strip() or "us-east-1"
        return self._settings
