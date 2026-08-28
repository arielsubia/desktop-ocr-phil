"""Recent-capture history management."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from .config import history_path


@dataclass
class HistoryEntry:
    """A single OCR capture result."""

    text: str
    engine: str
    timestamp: str
    line_count: int

    @classmethod
    def create(cls, text: str, engine: str) -> HistoryEntry:
        return cls(
            text=text,
            engine=engine,
            timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
            line_count=len(text.splitlines()) if text else 0,
        )


class History:
    """Persistent list of recent captures, newest first."""

    def __init__(self, max_entries: int = 20) -> None:
        self.max_entries = max_entries
        self._entries: list[HistoryEntry] = []
        self.load()

    @property
    def entries(self) -> list[HistoryEntry]:
        return list(self._entries)

    def add(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        del self._entries[self.max_entries :]
        self.save()

    def clear(self) -> None:
        self._entries.clear()
        self.save()

    def load(self) -> None:
        path = history_path()
        if not path.exists():
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            self._entries = [HistoryEntry(**item) for item in raw][: self.max_entries]
        except (OSError, ValueError, TypeError):
            self._entries = []

    def save(self) -> None:
        history_path().write_text(
            json.dumps([asdict(e) for e in self._entries], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
