"""Tests for the AWS OCR engine, adapting the previous project's Textract logic.

These use mocked boto3 clients, so no network or real credentials are needed.
"""

from __future__ import annotations

import pytest

from phildev_ocr.ocr.aws import AwsOcrEngine
from phildev_ocr.ocr.base import OcrError


class _FakeTextractClient:
    def detect_document_text(self, Document):  # noqa: N803 - boto3 kwarg name
        assert "Bytes" in Document
        return {
            "Blocks": [
                {"BlockType": "PAGE"},
                {"BlockType": "LINE", "Text": "Hello"},
                {"BlockType": "WORD", "Text": "ignored"},
                {"BlockType": "LINE", "Text": "World"},
            ]
        }


def test_textract_joins_line_blocks(monkeypatch):
    engine = AwsOcrEngine(backend="textract")
    monkeypatch.setattr(
        "boto3.client", lambda service, region_name=None: _FakeTextractClient()
    )
    result = engine.extract(b"fake-png-bytes")
    assert result.text == "Hello\nWorld"
    assert result.engine == "aws:textract"
    assert result.line_count == 2


def test_rejects_oversized_image():
    engine = AwsOcrEngine(backend="textract")
    with pytest.raises(OcrError, match="5MB"):
        engine.extract(b"x" * (5 * 1024 * 1024 + 1))
