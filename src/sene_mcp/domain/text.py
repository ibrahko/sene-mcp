"""Text helpers shared by the domain."""

from __future__ import annotations

import re
import unicodedata


def fold(text: str) -> str:
    """Lowercase, trim and strip accents: 'Ségou' -> 'segou', 'Émamectine' -> 'emamectine'."""
    decomposed = unicodedata.normalize("NFKD", text.strip())
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def short(value: str, limit: int = 60) -> str:
    """repr() of user input, truncated so error messages never echo huge payloads."""
    return repr(value if len(value) <= limit else value[:limit] + "…")


def without_parentheses(text: str) -> str:
    """'Marché de Mopti (démo)' -> 'Marché de Mopti'."""
    return re.sub(r"\s*\([^)]*\)", "", text).strip()
