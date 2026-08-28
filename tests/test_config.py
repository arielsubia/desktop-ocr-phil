"""Tests for settings persistence."""

from __future__ import annotations

from phildev_ocr.config import Settings


def test_defaults():
    settings = Settings()
    assert settings.ocr_engine == "tesseract"
    assert settings.hotkey == "<ctrl>+<shift>+x"
    assert settings.auto_copy is True


def test_save_and_load_round_trip():
    settings = Settings()
    settings.ocr_engine = "aws"
    settings.aws_region = "eu-west-1"
    settings.save()

    loaded = Settings.load()
    assert loaded.ocr_engine == "aws"
    assert loaded.aws_region == "eu-west-1"


def test_load_ignores_unknown_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from phildev_ocr.config import settings_path

    settings_path().write_text('{"ocr_engine": "aws", "bogus": 123}', encoding="utf-8")
    loaded = Settings.load()
    assert loaded.ocr_engine == "aws"
    assert not hasattr(loaded, "bogus")
