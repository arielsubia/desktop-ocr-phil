"""Global hotkey listener running on a background thread.

pynput callbacks fire on a listener thread, so the trigger is bridged to the Qt
main thread via a Qt signal.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class GlobalHotkey(QObject):
    """Listens for a global hotkey and emits ``triggered`` on the Qt thread."""

    triggered = pyqtSignal()

    def __init__(self, hotkey: str) -> None:
        super().__init__()
        self._hotkey = hotkey
        self._listener = None

    def start(self) -> None:
        from pynput import keyboard

        self.stop()
        self._listener = keyboard.GlobalHotKeys({self._hotkey: self._on_activate})
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def update_hotkey(self, hotkey: str) -> None:
        self._hotkey = hotkey
        self.start()

    def _on_activate(self) -> None:
        self.triggered.emit()
