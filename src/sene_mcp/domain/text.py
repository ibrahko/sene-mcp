"""Text helpers shared by the domain."""

from __future__ import annotations

import unicodedata


def fold(text: str) -> str:
    """Lowercase, trim and strip accents: 'Ségou' -> 'segou', 'Émamectine' -> 'emamectine'."""
    decomposed = unicodedata.normalize("NFKD", text.strip())
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()
