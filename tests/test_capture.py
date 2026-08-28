"""Tests for the capture overlay's DPI coordinate conversion.

These run headless (offscreen Qt platform, set in CI and the test command) and
never grab the real screen; they exercise only the logical->physical math.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QPoint, QRect

from phildev_ocr.capture import CaptureOverlay


@pytest.fixture
def overlay(qtbot):
    widget = CaptureOverlay()
    qtbot.addWidget(widget)
    return widget


def _fake_screen(monkeypatch, ratio: float, geo: QRect):
    screen = SimpleNamespace(
        devicePixelRatio=lambda: ratio,
        geometry=lambda: geo,
    )
    monkeypatch.setattr(
        "phildev_ocr.capture.QGuiApplication.screenAt", lambda _p: screen
    )
    monkeypatch.setattr(
        "phildev_ocr.capture.QGuiApplication.primaryScreen", lambda: screen
    )


def test_physical_conversion_at_100_percent(overlay, monkeypatch):
    overlay._virtual_geo = QRect(0, 0, 1920, 1080)
    _fake_screen(monkeypatch, ratio=1.0, geo=QRect(0, 0, 1920, 1080))
    # QRect(x, y, w, h): explicit width/height avoid the point-to-point +1px.
    rect = QRect(100, 200, 200, 60)
    phys = overlay._to_physical(rect)
    assert phys == {"left": 100, "top": 200, "width": 200, "height": 60}


def test_physical_conversion_at_150_percent(overlay, monkeypatch):
    # A 150%-scaled 1280x720 logical desktop maps to 1920x1080 physical.
    overlay._virtual_geo = QRect(0, 0, 1280, 720)
    _fake_screen(monkeypatch, ratio=1.5, geo=QRect(0, 0, 1280, 720))
    rect = QRect(100, 100, 200, 100)
    phys = overlay._to_physical(rect)
    assert phys == {"left": 150, "top": 150, "width": 300, "height": 150}


def test_width_and_height_never_zero(overlay, monkeypatch):
    overlay._virtual_geo = QRect(0, 0, 1920, 1080)
    _fake_screen(monkeypatch, ratio=1.0, geo=QRect(0, 0, 1920, 1080))
    phys = overlay._to_physical(QRect(QPoint(10, 10), QPoint(10, 10)))
    assert phys["width"] >= 1
    assert phys["height"] >= 1
