"""Tests for the Tesseract engine availability logic."""

from __future__ import annotations

import pytest

from phildev_ocr.ocr.base import OcrError
from phildev_ocr.ocr.tesseract import TesseractEngine


def test_unavailable_when_binary_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _name: None)
    monkeypatch.setattr("pathlib.Path.exists", lambda _self: False)
    engine = TesseractEngine()
    available, message = engine.is_available()
    assert available is False
    assert "Tesseract" in message


def test_extract_raises_when_unavailable(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _name: None)
    monkeypatch.setattr("pathlib.Path.exists", lambda _self: False)
    engine = TesseractEngine()
    with pytest.raises(OcrError):
        engine.extract(b"fake")


def test_explicit_cmd_is_used():
    engine = TesseractEngine(cmd=r"C:\custom\tesseract.exe")
    available, _ = engine.is_available()
    assert available is True
    assert engine.cmd == r"C:\custom\tesseract.exe"
