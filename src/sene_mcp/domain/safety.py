"""Safety guardrails for crop-protection content.

The service never tells a farmer which chemical to use or how much. These checks
run in CI on every pest sheet, and (in lot 3) on the agent's final answers.
"""

from __future__ import annotations

import re

from sene_mcp.domain.text import fold

# The one sentence every sheet must use for treatments.
TREATMENT_GUIDANCE = (
    "Pour tout traitement, contactez le service agricole ou l'agent de vulgarisation de votre zone."
)

# Dosage patterns: "2 g/l", "50 ml / ha", "1,5 kg par hectare", "10 cc/pompe"...
_DOSAGE = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:g|kg|mg|ml|l|cl|cc|litres?)\s*(?:/|par|per)\s*"
    r"(?:l|litres?|ha|hectares?|pompes?|pulverisateurs?|sprayers?|m2)\b",
    re.IGNORECASE,
)

_DOSAGE_WORDS = re.compile(r"\b(?:dose|doses|dosage|posologie)\b", re.IGNORECASE)

# Common active ingredients and pesticide families. Not exhaustive: the goal is to
# catch an obvious slip, the real protection is that sheets are written by hand.
_ACTIVE_INGREDIENTS = (
    "emamectine",
    "emamectin",
    "chlorpyrifos",
    "cypermethrine",
    "cypermethrin",
    "lambda-cyhalothrine",
    "lambda-cyhalothrin",
    "deltamethrine",
    "deltamethrin",
    "spinetoram",
    "spinosad",
    "chlorantraniliprole",
    "carbofuran",
    "imidaclopride",
    "imidacloprid",
    "acetamipride",
    "acetamiprid",
    "glyphosate",
    "atrazine",
    "mancozebe",
    "mancozeb",
    "tricyclazole",
    "dimethoate",
    "malathion",
    "fipronil",
)


def find_violations(text: str) -> list[str]:
    """Return a human-readable list of forbidden content found in `text`."""
    folded = fold(text)
    violations: list[str] = []
    for match in _DOSAGE.finditer(folded):
        violations.append(f"dosage: {match.group(0)!r}")
    for match in _DOSAGE_WORDS.finditer(folded):
        violations.append(f"dosage word: {match.group(0)!r}")
    for name in _ACTIVE_INGREDIENTS:
        if re.search(rf"\b{re.escape(name)}\b", folded):
            violations.append(f"active ingredient: {name!r}")
    return violations


def is_safe(text: str) -> bool:
    return not find_violations(text)
