"""Clipboard helper."""

from __future__ import annotations


def copy_text(text: str) -> bool:
    """Copy text to the clipboard. Returns True on success."""
    if not text:
        return False
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:  # noqa: BLE001 - clipboard access can fail on headless systems
        return False
