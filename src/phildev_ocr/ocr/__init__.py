"""OCR engines: offline (Tesseract) and cloud (AWS Textract / Bedrock)."""

from __future__ import annotations

from ..config import Settings
from .base import OcrEngine, OcrError, OcrResult


def build_engine(settings: Settings) -> OcrEngine:
    """Factory: build the OCR engine selected in settings.

    Imports are deferred so that, for example, the Tesseract path does not
    require boto3 to be importable and vice versa.
    """
    if settings.ocr_engine == "aws":
        from .aws import AwsOcrEngine

        return AwsOcrEngine(
            region=settings.aws_region,
            backend=settings.aws_backend,
        )
    from .tesseract import TesseractEngine

    return TesseractEngine(
        lang=settings.tesseract_lang,
        cmd=settings.tesseract_cmd or None,
    )


__all__ = ["OcrEngine", "OcrError", "OcrResult", "build_engine"]
