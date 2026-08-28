"""Offline OCR engine backed by Tesseract via pytesseract."""

from __future__ import annotations

import io
import shutil

from .base import OcrEngine, OcrError, OcrResult

_COMMON_WINDOWS_PATHS = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
)


def _resolve_tesseract_cmd(explicit: str | None) -> str | None:
    """Locate the tesseract binary from an explicit path, PATH, or common dirs."""
    if explicit:
        return explicit
    found = shutil.which("tesseract")
    if found:
        return found
    from pathlib import Path

    for candidate in _COMMON_WINDOWS_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


class TesseractEngine(OcrEngine):
    """Runs OCR locally with no network access."""

    name = "tesseract"

    def __init__(self, lang: str = "eng", cmd: str | None = None) -> None:
        self.lang = lang
        self.cmd = _resolve_tesseract_cmd(cmd)

    def is_available(self) -> tuple[bool, str]:
        if self.cmd is None:
            return (
                False,
                "Tesseract was not found. Install it and add it to PATH, or set the "
                "path in Settings. See the README for install instructions.",
            )
        return True, "Tesseract is available."

    def extract(self, image_bytes: bytes) -> OcrResult:
        available, message = self.is_available()
        if not available:
            raise OcrError(message)

        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise OcrError(f"Missing OCR dependency: {exc}") from exc

        pytesseract.pytesseract.tesseract_cmd = self.cmd
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                text = pytesseract.image_to_string(image, lang=self.lang)
        except pytesseract.TesseractError as exc:
            raise OcrError(f"Tesseract failed: {exc}") from exc
        except OSError as exc:
            raise OcrError(f"Could not read captured image: {exc}") from exc

        return OcrResult(text=text.strip(), engine=self.name)
