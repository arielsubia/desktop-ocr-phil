"""Screen capture: a transparent full-screen overlay for selecting a region.

The overlay spans all monitors (the virtual desktop). The user drags a
rectangle; on release the selected region is grabbed with ``mss`` and encoded
as PNG bytes, which the OCR engines consume directly.

Qt reports geometry and mouse positions in *logical* (DPI-scaled) pixels, while
``mss`` grabs in *physical* pixels. On any display whose scaling is not 100%,
passing logical coordinates straight to mss captures the wrong (shifted,
smaller) region. We therefore convert the selected rectangle to physical
coordinates using the device pixel ratio before grabbing.
"""

from __future__ import annotations

import io

from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QKeyEvent, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from .branding import ACCENT


def _grab_region_png(left: int, top: int, width: int, height: int) -> bytes:
    """Grab a physical-pixel screen region and return PNG-encoded bytes."""
    import mss
    from PIL import Image

    with mss.mss() as sct:
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
    image = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class CaptureOverlay(QWidget):
    """Full-virtual-desktop overlay that emits PNG bytes of the selected area."""

    region_captured = pyqtSignal(bytes)
    cancelled = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._origin = None
        self._current = None
        self._virtual_geo = QRect()

    def start(self) -> None:
        """Size the overlay to cover the whole virtual desktop and show it."""
        geo = QRect()
        for screen in QGuiApplication.screens():
            geo = geo.united(screen.geometry())
        self._virtual_geo = geo
        self.setGeometry(geo)
        self._origin = None
        self._current = None
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    # --- Mouse interaction ---
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._current = self._origin
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._origin is not None:
            self._current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        rect = QRect(self._origin, self._current).normalized()
        self.hide()
        if rect.width() < 3 or rect.height() < 3:
            self.cancelled.emit()
            return

        try:
            phys = self._to_physical(rect)
            png = _grab_region_png(**phys)
        except Exception as exc:  # noqa: BLE001 - surface capture failure to the UI
            self.failed.emit(f"Screen capture failed: {exc}")
            return
        self.region_captured.emit(png)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()

    # --- Coordinate conversion ---
    def _to_physical(self, rect: QRect) -> dict[str, int]:
        """Convert an overlay-local logical rect to physical screen pixels.

        The selection midpoint decides which screen (and thus which device
        pixel ratio and physical origin) applies.
        """
        # Point in global logical coordinates (overlay origin + local offset).
        global_x = self._virtual_geo.x() + rect.x()
        global_y = self._virtual_geo.y() + rect.y()
        mid = rect.center()
        screen = QGuiApplication.screenAt(
            self._virtual_geo.topLeft() + mid
        ) or QGuiApplication.primaryScreen()

        ratio = screen.devicePixelRatio()
        s_geo = screen.geometry()  # logical geometry of this screen

        # Offset within the screen, scaled to physical pixels, added to the
        # screen's physical origin (logical origin * ratio approximates it for
        # standard multi-monitor layouts).
        phys_left = round(s_geo.x() * ratio + (global_x - s_geo.x()) * ratio)
        phys_top = round(s_geo.y() * ratio + (global_y - s_geo.y()) * ratio)
        return {
            "left": phys_left,
            "top": phys_top,
            "width": max(1, round(rect.width() * ratio)),
            "height": max(1, round(rect.height() * ratio)),
        }

    # --- Painting ---
    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 35, 110))
        if self._origin is not None and self._current is not None:
            rect = QRect(self._origin, self._current).normalized()
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Clear
            )
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            pen = QPen(QColor(ACCENT))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect)
