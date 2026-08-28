"""Application configuration and persistence.

Settings and history are stored under the user's local app data directory so the
packaged .exe does not need write access to its install location.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_DIR_NAME = "PhilDevDesktopOCR"


def app_data_dir() -> Path:
    """Return the per-user app data directory, creating it if needed."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = Path(base) / APP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_path() -> Path:
    return app_data_dir() / "settings.json"


def history_path() -> Path:
    return app_data_dir() / "history.json"


@dataclass
class Settings:
    """User-configurable settings."""

    hotkey: str = "<ctrl>+<shift>+x"
    ocr_engine: str = "tesseract"  # "tesseract" (offline) or "aws" (cloud)
    aws_region: str = "us-east-1"
    aws_backend: str = "textract"  # "textract" or "bedrock"
    tesseract_lang: str = "eng"
    tesseract_cmd: str = ""  # optional explicit path to tesseract.exe
    max_history: int = 20
    auto_copy: bool = True
    history: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls) -> Settings:
        path = settings_path()
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        known = {f: data[f] for f in cls().__dataclass_fields__ if f in data}
        return cls(**known)

    def save(self) -> None:
        settings_path().write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
