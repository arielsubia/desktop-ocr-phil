"""Application entry point: build the QApplication and show the tray app."""

from __future__ import annotations

import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .branding import APP_NAME, ORG_NAME, build_stylesheet, logo_path
from .config import Settings
from .ui.main_window import MainWindow


def run() -> int:
    """Start the Phil Dev Desktop OCR application."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setWindowIcon(QIcon(str(logo_path())))
    app.setStyleSheet(build_stylesheet())
    # Keep running while only the tray icon is visible.
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            APP_NAME,
            "No system tray is available on this system. The app cannot run.",
        )
        return 1

    settings = Settings.load()
    window = MainWindow(settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
