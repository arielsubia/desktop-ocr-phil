"""Application entry point: build the QApplication and show the tray app."""

from __future__ import annotations

import signal
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .branding import APP_NAME, ORG_NAME, build_stylesheet, logo_path
from .config import Settings
from .ui.main_window import MainWindow


def run() -> int:
    """Start the Phil Dev Desktop OCR application."""
    # Use exact (non-rounded) device pixel ratios so the capture overlay can
    # convert logical selection coordinates to physical pixels precisely on
    # displays with fractional scaling (e.g. 125%, 150%).
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
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

    # Let Ctrl+C in the launching terminal stop the app. Qt's C++ event loop
    # normally swallows SIGINT, so restore Python's default handler and pulse a
    # timer to give the interpreter a chance to run the handler.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    keep_alive = QTimer()
    keep_alive.start(250)
    keep_alive.timeout.connect(lambda: None)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
