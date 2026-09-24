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

_NUMBER = r"(?:\d+(?:[.,]\d+)?|un|une|un demi|une demie?|demi|deux|trois|quatre|cinq)"
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
# How the two are linked: "/", "par", "pour", "dans", "à l'", "au"...
_LINK = r"(?:/|par|per|pour|for|dans|in|a l'|a la|au|a)"
# "2 g/l", "50 ml / ha", "1,5 kg par hectare", "20 ml pour 15 litres d'eau",
# "20 ml de produit pour 15 litres", "40 ml/15 l", "1 sachet par pompe", "0,5 L/acre",
# "250 g à l'hectare", "un demi-litre par hectare"...
# The target must not be an elided article ("pour l'eau" is not "pour 1 l").
_DOSAGE = re.compile(
    rf"\b{_NUMBER}[\s-]*{_QUANTITY}\s*(?:a (?:soupe|cafe)\s+)?"
    rf"(?:(?:de|d'|du|des|of)\s*[a-z]+\s+)?{_LINK}\s*"
    rf"(?:\d+(?:[.,]\d+)?\s*|(?:un|une|a|one|le|la|chaque|each)\s+)?"
    rf"(?:(?:d'|de |du |of )\s*)?{_TARGET}\b(?!['\u2019])"
)
_DOSAGE_WORDS = re.compile(r"\b(?:doses?|dosages?|posologie)\b")


def _normalize(text: str) -> str:
    """Fold case and accents, and turn any punctuation run into a single space."""
    return re.sub(r"[^a-z0-9]+", " ", fold(text)).strip()


@cache
def _forbidden_words() -> tuple[tuple[re.Pattern[str], ...], tuple[re.Pattern[str], ...]]:
    """(patterns on normalized text, raw patterns on folded text).

    A plain line is a stem: matched on normalized text, with an optional final "e", and
    the space between words optional ("lambda cyhalothrin" also catches
    "lambdacyhalothrine"). A line starting with "re:" is a regular expression applied to
    folded text, for names that normalization would break (e.g. "2,4-D").
    """
    raw = resources.files("sene_mcp.knowledge").joinpath("forbidden_products.txt")
    stems: list[re.Pattern[str]] = []
    regexes: list[re.Pattern[str]] = []
    for line in raw.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        if entry.startswith("re:"):
            regexes.append(re.compile(entry[3:].strip()))
        else:
            words = [re.escape(w) for w in _normalize(entry).split()]
            stems.append(re.compile(rf"\b{' ?'.join(words)}e?\b"))
    return tuple(stems), tuple(regexes)


def find_violations(text: str) -> list[str]:
    """Return a human-readable list of forbidden content found in `text`."""
    folded = fold(text)
    violations = [f"dosage: {m.group(0)!r}" for m in _DOSAGE.finditer(folded)]
    violations += [f"dosage word: {m.group(0)!r}" for m in _DOSAGE_WORDS.finditer(folded)]
    stems, regexes = _forbidden_words()
    normalized = _normalize(text)
    violations += [f"product: {p.pattern!r}" for p in stems if p.search(normalized)]
    violations += [f"product: {p.pattern!r}" for p in regexes if p.search(folded)]
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
