"""Safety guardrails for crop-protection content.

The service never tells a farmer which chemical to use or how much. These checks run
when pest sheets are loaded, in CI on every sheet and tool output, and (in lot 3) on the
agent's final answers.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from functools import cache
from importlib import resources
from typing import Any

from sene_mcp.domain.text import fold

# The one sentence every sheet must use for treatments.
TREATMENT_GUIDANCE = (
    "Pour tout traitement, contactez le service agricole ou l'agent de vulgarisation de votre zone."
)

_NUMBER = r"\d+(?:[.,]\d+)?"
# What is measured out: weights, volumes, and the containers used on the field.
_QUANTITY = (
    r"(?:g|kg|mg|ml|l|cl|cc|litres?|liters?|sachets?|bidons?|boites?|cuilleres?|"
    r"capsules?|bouchons?|verres?)"
)
# What it is measured against: water, a sprayer, a surface, seed.
_TARGET = (
    r"(?:l|litres?|liters?|ha|hectares?|acres?|m2|pompes?|pulverisateurs?|sprayers?|"
    r"bidons?|seaux?|kg)"
)
# "2 g/l", "50 ml / ha", "1,5 kg par hectare", "20 ml pour 15 litres d'eau",
# "40 ml/15 l", "1 sachet par pompe", "0,5 L/acre"...
_DOSAGE = re.compile(
    rf"{_NUMBER}\s*{_QUANTITY}\s*(?:/|par|per|pour|for)\s*"
    rf"(?:{_NUMBER}\s*|(?:un|une|a|one|le|la|chaque|each)\s+)?"
    rf"(?:(?:d'|de |du |of )\s*)?{_TARGET}\b"
)
_DOSAGE_WORDS = re.compile(r"\b(?:doses?|dosages?|posologie)\b")


def _normalize(text: str) -> str:
    """Fold case and accents, and turn any punctuation run into a single space."""
    return re.sub(r"[^a-z0-9]+", " ", fold(text)).strip()


@cache
def _forbidden_words() -> tuple[re.Pattern[str], ...]:
    raw = resources.files("sene_mcp.knowledge").joinpath("forbidden_products.txt")
    patterns = []
    for line in raw.read_text(encoding="utf-8").splitlines():
        word = line.strip()
        if word and not word.startswith("#"):
            stem = _normalize(word)
            patterns.append(re.compile(rf"\b{re.escape(stem)}e?\b"))
    return tuple(patterns)


def find_violations(text: str) -> list[str]:
    """Return a human-readable list of forbidden content found in `text`."""
    folded = fold(text)
    violations = [f"dosage: {m.group(0)!r}" for m in _DOSAGE.finditer(folded)]
    violations += [f"dosage word: {m.group(0)!r}" for m in _DOSAGE_WORDS.finditer(folded)]
    normalized = _normalize(text)
    violations += [f"product: {p.pattern!r}" for p in _forbidden_words() if p.search(normalized)]
    return violations


def is_safe(text: str) -> bool:
    return not find_violations(text)


def iter_strings(value: Any, path: str = "") -> Iterator[tuple[str, str]]:
    """Yield (path, text) for every string nested in dicts and lists."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")


def find_violations_in(data: Any) -> list[str]:
    """Check every string in a nested structure (a raw sheet, a tool output)."""
    return [
        f"{path}: {violation}"
        for path, text in iter_strings(data)
        for violation in find_violations(text)
    ]
