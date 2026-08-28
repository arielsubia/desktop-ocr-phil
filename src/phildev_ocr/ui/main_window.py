"""Main window: recent-capture history plus the tray-driven capture flow."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..branding import APP_NAME, ORG_NAME, TEXT_SECONDARY, logo_path
from ..capture import CaptureOverlay
from ..clipboard import copy_text
from ..config import Settings
from ..history import History, HistoryEntry
from ..hotkey import GlobalHotkey
from ..worker import OcrRunner
from .about import AboutDialog
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Controls the full flow: hotkey -> overlay -> OCR -> clipboard -> history."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.history = History(max_entries=settings.max_history)
        self.runner = OcrRunner()
        self.overlay = CaptureOverlay()
        self.hotkey = GlobalHotkey(settings.hotkey)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(logo_path())))
        self.resize(720, 560)
        self.setMinimumSize(560, 420)

        self._build_ui()
        self._build_tray()
        self._wire_signals()
        self._refresh_history()

        self.hotkey.start()

    # --- UI construction ---
    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        self.capture_btn = QPushButton("Capture (or press hotkey)")
        self.capture_btn.clicked.connect(self.trigger_capture)
        header.addWidget(self.capture_btn)
        layout.addLayout(header)

        engine_label = QLabel(self._engine_summary())
        engine_label.setObjectName("secondary")
        self.engine_label = engine_label
        layout.addWidget(engine_label)

        # Two-column body: compact history on the left, the editable text on
        # the right as the primary area.
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_history_panel())
        splitter.addWidget(self._build_editor_panel())
        # The editor stays the growing pane; the history keeps its width.
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([220, 500])
        layout.addWidget(splitter, stretch=1)

        footer = QHBoxLayout()
        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("secondary")
        settings_btn.clicked.connect(self.open_settings)
        about_btn = QPushButton("About")
        about_btn.setObjectName("secondary")
        about_btn.clicked.connect(self.open_about)
        footer.addWidget(settings_btn)
        footer.addStretch()
        footer.addWidget(about_btn)
        layout.addLayout(footer)

        credit = QLabel(f"A {ORG_NAME} project")
        credit.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(credit, alignment=Qt.AlignmentFlag.AlignRight)

        self.setCentralWidget(central)

    def _build_history_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("historyPanel")
        col = QVBoxLayout(panel)
        col.setContentsMargins(12, 12, 12, 12)
        col.setSpacing(8)

        history_label = QLabel("Recent captures")
        history_label.setObjectName("historyTitle")
        col.addWidget(history_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setMaximumWidth(240)
        # Clicking an entry loads its text into the editor for review/editing.
        self.history_list.itemClicked.connect(self._load_selected)
        col.addWidget(self.history_list, stretch=1)

        clear_btn = QPushButton("Clear history")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._clear_history)
        col.addWidget(clear_btn)
        return panel

    def _build_editor_panel(self) -> QWidget:
        panel = QWidget()
        col = QVBoxLayout(panel)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)

        col.addWidget(QLabel("Extracted text"))
        # The primary area: large and editable so the user can fix anything the
        # OCR got wrong (e.g. line breaks) before copying it elsewhere.
        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setReadOnly(False)
        self.editor.setPlaceholderText("Extracted text appears here. You can edit it.")
        self.editor.setAcceptRichText(False)
        col.addWidget(self.editor, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy_editor)
        actions.addWidget(self.copy_btn)
        col.addLayout(actions)
        return panel

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(QIcon(str(logo_path())), self)
        self.tray.setToolTip(APP_NAME)
        menu = QMenu()

        capture_action = QAction("Capture", self)
        capture_action.triggered.connect(self.trigger_capture)
        show_action = QAction("Show window", self)
        show_action.triggered.connect(self._show_window)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)

        menu.addAction(capture_action)
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addAction(about_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _wire_signals(self) -> None:
        self.hotkey.triggered.connect(self.trigger_capture)
        self.overlay.region_captured.connect(self._on_region_captured)
        self.overlay.cancelled.connect(self._on_capture_cancelled)
        self.overlay.failed.connect(self._on_ocr_failed)
        self.runner.finished.connect(self._on_ocr_finished)
        self.runner.failed.connect(self._on_ocr_failed)

    # --- Capture flow ---
    def trigger_capture(self) -> None:
        self.capture_btn.setEnabled(False)
        self.hide()
        QApplication.processEvents()
        self.overlay.start()

    def _on_capture_cancelled(self) -> None:
        self.capture_btn.setEnabled(True)
        self._show_window()

    def _on_region_captured(self, image_bytes: bytes) -> None:
        # Bring the window back so the user sees progress and the result.
        self._show_window()
        self.editor.setPlaceholderText("Extracting text...")
        self.editor.clear()
        self.runner.submit(image_bytes, self.settings)

    def _on_ocr_finished(self, text: str, engine: str) -> None:
        self.capture_btn.setEnabled(True)
        entry = HistoryEntry.create(text=text, engine=engine)
        self.history.add(entry)
        self._refresh_history()
        self.editor.setPlainText(text or "(no text detected)")

        if self.settings.auto_copy and text:
            copy_text(text)

    def _on_ocr_failed(self, message: str) -> None:
        self.capture_btn.setEnabled(True)
        self.editor.setPlaceholderText("Extracted text appears here. You can edit it.")
        self._show_window()
        QMessageBox.warning(self, "OCR failed", message)

    # --- History ---
    def _refresh_history(self) -> None:
        self.history_list.clear()
        for entry in self.history.entries:
            snippet = entry.text.replace("\n", " ").strip()
            if len(snippet) > 70:
                snippet = snippet[:67] + "..."
            label = f"[{entry.timestamp}] {snippet or '(empty)'}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, entry.text)
            self.history_list.addItem(item)

    def _load_selected(self, item: QListWidgetItem) -> None:
        """Load a history entry into the editor for review and editing."""
        text = item.data(Qt.ItemDataRole.UserRole)
        if text is not None:
            self.editor.setPlainText(text)

    def _copy_editor(self) -> None:
        """Copy the current (possibly edited) editor content to the clipboard."""
        text = self.editor.toPlainText()
        if text and copy_text(text):
            self._flash_copied()

    def _flash_copied(self) -> None:
        """Give brief in-button feedback instead of a system notification."""
        self.copy_btn.setText("Copied")
        self.copy_btn.setEnabled(False)
        QTimer.singleShot(1000, self._reset_copy_button)

    def _reset_copy_button(self) -> None:
        self.copy_btn.setText("Copy")
        self.copy_btn.setEnabled(True)

    def _clear_history(self) -> None:
        self.history.clear()
        self._refresh_history()

    # --- Dialogs ---
    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings = dialog.result_settings()
            self.settings.save()
            self.hotkey.update_hotkey(self.settings.hotkey)
            self.engine_label.setText(self._engine_summary())

    def open_about(self) -> None:
        AboutDialog(self).exec()

    def _engine_summary(self) -> str:
        if self.settings.ocr_engine == "aws":
            return f"Engine: AWS {self.settings.aws_backend} ({self.settings.aws_region})"
        return f"Engine: Tesseract offline ({self.settings.tesseract_lang})"

    # --- Window / tray behavior ---
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:
        """Closing the window hides it to the tray instead of quitting."""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            APP_NAME,
            "Still running in the tray. Use the tray menu to quit.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def quit_app(self) -> None:
        self.hotkey.stop()
        self.tray.hide()
        QGuiApplication.instance().quit()
