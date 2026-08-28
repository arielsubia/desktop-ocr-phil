"""Phil Dev brand identity: color palette, fonts, and asset paths."""

from __future__ import annotations

from pathlib import Path

# --- Color palette (Phil Dev) ---
BG_PRIMARY = "#f5f5f7"
BG_SECONDARY = "#ffffff"
BG_CARD = "#e8e8ec"
ACCENT = "#d4768a"
ACCENT_HOVER = "#e0899b"
TEXT_PRIMARY = "#4a4a55"
TEXT_SECONDARY = "#7a7a88"
BORDER = "#d9d9e0"
SURFACE_DARK = "#5c5c6b"
SURFACE_DARKER = "#4a4a55"

FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

ORG_NAME = "Phil Dev"
APP_NAME = "Phil Dev Desktop OCR"


def logo_path() -> Path:
    """Return the absolute path to the bundled Phil Dev logo."""
    return Path(__file__).resolve().parent / "assets" / "logo-phildev.png"


def build_stylesheet() -> str:
    """Build the Qt stylesheet applying the Phil Dev palette."""
    return f"""
        QWidget {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            font-family: {FONT_STACK};
            font-size: 13px;
        }}
        QMainWindow, QDialog {{
            background-color: {BG_PRIMARY};
        }}
        QLabel#secondary {{
            color: {TEXT_SECONDARY};
        }}
        QFrame#card, QListWidget {{
            background-color: {BG_SECONDARY};
            border: 1px solid {BORDER};
            border-radius: 8px;
        }}
        QPushButton {{
            background-color: {ACCENT};
            color: {BG_SECONDARY};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton:disabled {{
            background-color: {BORDER};
            color: {TEXT_SECONDARY};
        }}
        QPushButton#secondary {{
            background-color: {BG_CARD};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
        }}
        QComboBox, QLineEdit {{
            background-color: {BG_SECONDARY};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 6px 8px;
        }}
        QMenuBar, QMenu {{
            background-color: {SURFACE_DARKER};
            color: {BG_SECONDARY};
        }}
        QMenu::item:selected {{
            background-color: {ACCENT};
        }}
        /* Recent captures: dark panel with light text. */
        QWidget#historyPanel {{
            background-color: {SURFACE_DARK};
            border-radius: 8px;
        }}
        QLabel#historyTitle {{
            color: {BG_SECONDARY};
            font-weight: 600;
            background: transparent;
            padding: 2px 2px 6px 2px;
        }}
        QListWidget#historyList {{
            background-color: {SURFACE_DARK};
            color: {BG_SECONDARY};
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 6px;
            padding: 2px;
        }}
        QListWidget#historyList::item {{
            padding: 4px 2px;
            border-radius: 4px;
        }}
        QListWidget#historyList::item:hover {{
            background-color: rgba(255, 255, 255, 0.08);
        }}
        QListWidget#historyList::item:selected {{
            background-color: {ACCENT};
            color: {BG_SECONDARY};
        }}
        /* Extracted text: primary white surface. */
        QTextEdit#editor {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 6px;
        }}
    """
