"""About dialog with Phil Dev branding."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..branding import APP_NAME, ORG_NAME, TEXT_SECONDARY, logo_path


class AboutDialog(QDialog):
    """Shows app name, version, and the Phil Dev logo (transparent, no white box)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        logo = QLabel()
        pixmap = QPixmap(str(logo_path()))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaledToHeight(
                    48, Qt.TransformationMode.SmoothTransformation
                )
            )
        # Keep the transparent background; do not paint a surface behind it.
        logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        header.addWidget(logo)

        title_box = QVBoxLayout()
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        version = QLabel(f"Version {__version__}")
        version.setObjectName("secondary")
        title_box.addWidget(title)
        title_box.addWidget(version)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        desc = QLabel(
            "Capture a screen region and extract its text with OCR.\n"
            "Offline with Tesseract, or in the cloud with AWS."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        credit = QLabel(f"A {ORG_NAME} project")
        credit.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(credit)

        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignRight)
