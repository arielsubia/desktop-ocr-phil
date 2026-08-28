"""Shared OCR engine contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class OcrError(Exception):
    """Raised when an OCR engine fails or is unavailable."""


@dataclass
class OcrResult:
    """Result of an OCR run."""

    text: str
    engine: str

    @property
    def line_count(self) -> int:
        return len(self.text.splitlines()) if self.text else 0


class OcrEngine(ABC):
    """Common interface for OCR backends."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """Return (available, message). Message explains why it is unavailable."""

    @abstractmethod
    def extract(self, image_bytes: bytes) -> OcrResult:
        """Extract text from PNG-encoded image bytes."""
