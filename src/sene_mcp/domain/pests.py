"""Pest use cases. Lot 1: sheet lookup. Lot 2 adds symptom matching."""

from __future__ import annotations

from sene_mcp.domain.models import Crop, DomainError, PestSheet
from sene_mcp.ports.knowledge import KnowledgeBase


def parse_crop(value: str) -> Crop:
    try:
        return Crop(value.strip().lower())
    except ValueError:
        known = ", ".join(c.value for c in Crop)
        raise DomainError("UNKNOWN_CROP", f"{value!r} is not covered. Known: {known}.") from None


def get_pest_sheet(kb: KnowledgeBase, sheet_id: str) -> PestSheet:
    sheet = kb.get(sheet_id.strip())
    if sheet is None:
        raise DomainError("NOT_FOUND", f"No pest sheet with id {sheet_id!r}.")
    return sheet
