"""Background OCR worker so the UI thread never blocks on capture processing.

The task keeps a reference to itself alive in the runner until it finishes, so
the ``QRunnable`` and its signal object are never garbage-collected mid-flight
(which previously caused a native crash when the result signal crossed threads).
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from .config import Settings
from .ocr import OcrError, build_engine


class _WorkerSignals(QObject):
    finished = pyqtSignal(str, str)  # text, engine
    failed = pyqtSignal(str)  # error message


class _OcrTask(QRunnable):
    def __init__(self, image_bytes: bytes, settings: Settings) -> None:
        super().__init__()
        self._image_bytes = image_bytes
        self._settings = settings
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            engine = build_engine(self._settings)
            result = engine.extract(self._image_bytes)
        except OcrError as exc:
            self.signals.failed.emit(str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - report unexpected failures to UI
            self.signals.failed.emit(f"Unexpected error: {exc}")
            return
        self.signals.finished.emit(result.text, result.engine)


class OcrRunner(QObject):
    """Runs OCR tasks on a thread pool and relays results as signals."""

    finished = pyqtSignal(str, str)
    failed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._pool = QThreadPool.globalInstance()
        # Hold strong references to in-flight tasks so neither the QRunnable nor
        # its signal object is collected while the worker thread is running.
        self._active: set[_OcrTask] = set()

    def submit(self, image_bytes: bytes, settings: Settings) -> None:
        task = _OcrTask(image_bytes, settings)
        self._active.add(task)
        task.signals.finished.connect(self.finished)
        task.signals.failed.connect(self.failed)
        # Drop the reference only after the result has been delivered.
        task.signals.finished.connect(lambda *_: self._active.discard(task))
        task.signals.failed.connect(lambda *_: self._active.discard(task))
        self._pool.start(task)
