"""Tests for the capture history."""

from __future__ import annotations

from phildev_ocr.history import History, HistoryEntry


def test_entry_create_counts_lines():
    entry = HistoryEntry.create(text="line one\nline two", engine="tesseract")
    assert entry.line_count == 2
    assert entry.engine == "tesseract"
    assert entry.timestamp


def test_add_prepends_newest_first():
    history = History(max_entries=5)
    history.add(HistoryEntry.create("first", "tesseract"))
    history.add(HistoryEntry.create("second", "tesseract"))
    assert history.entries[0].text == "second"
    assert history.entries[1].text == "first"


def test_max_entries_enforced():
    history = History(max_entries=2)
    for i in range(5):
        history.add(HistoryEntry.create(f"entry {i}", "tesseract"))
    assert len(history.entries) == 2
    assert history.entries[0].text == "entry 4"


def test_persistence_round_trip():
    history = History(max_entries=5)
    history.add(HistoryEntry.create("persisted", "tesseract"))

    reloaded = History(max_entries=5)
    assert reloaded.entries[0].text == "persisted"


def test_clear_empties_history():
    history = History(max_entries=5)
    history.add(HistoryEntry.create("gone", "tesseract"))
    history.clear()
    assert history.entries == []
