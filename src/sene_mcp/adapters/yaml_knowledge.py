"""Pest sheets stored as one YAML file each, versioned with the code."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from sene_mcp.domain.models import (
    Crop,
    Management,
    PestKind,
    PestNames,
    PestSheet,
    ReviewStatus,
    Severity,
    Source,
)
from sene_mcp.domain.safety import TREATMENT_GUIDANCE, find_violations_in


class SheetFormatError(ValueError):
    """A sheet file is missing a field or has an invalid value."""


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def parse_sheet(data: dict[str, Any], origin: str = "<memory>") -> PestSheet:
    try:
        names = data["names"]
        management = data.get("management") or {}
        sources = data.get("sources") or []
        return PestSheet(
            id=str(data["id"]),
            crops=tuple(Crop(c) for c in data["crops"]),
            names=PestNames(
                fr=str(names["fr"]),
                scientific=str(names["scientific"]),
                bm=names.get("bm"),
            ),
            kind=PestKind(data["kind"]),
            symptoms=tuple(str(s) for s in data["symptoms"]),
            keywords=tuple(str(k) for k in data.get("keywords") or ()),
            season=str(data.get("season", "")),
            severity=Severity(data["severity"]),
            management=Management(
                prevention=tuple(management.get("prevention") or ()),
                cultural=tuple(management.get("cultural") or ()),
                biological=tuple(management.get("biological") or ()),
            ),
            treatment_guidance=" ".join(str(data["treatment_guidance"]).split()),
            sources=tuple(
                Source(
                    title=str(s["title"]),
                    publisher=str(s["publisher"]),
                    url=str(s["url"]),
                    consulted_on=_as_date(s["consulted_on"]),
                )
                for s in sources
            ),
            review_status=ReviewStatus(data["review_status"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SheetFormatError(f"{origin}: invalid pest sheet ({exc})") from exc


def check_sheet_safety(data: dict[str, Any], origin: str = "<memory>") -> None:
    """Refuse a sheet that contains a dose or a product name, in any field.

    `treatment_guidance` is exempt from the scan but must be the fixed referral text.
    """
    content = {k: v for k, v in data.items() if k != "treatment_guidance"}
    violations = find_violations_in(content)
    if violations:
        raise SheetFormatError(f"{origin}: forbidden content: {'; '.join(violations)}")
    guidance = " ".join(str(data.get("treatment_guidance", "")).split())
    if guidance != TREATMENT_GUIDANCE:
        raise SheetFormatError(f"{origin}: treatment_guidance must be the fixed referral text")


class YamlKnowledgeBase:
    def __init__(self, directory: Path) -> None:
        self._sheets: dict[str, PestSheet] = {}
        for path in sorted(directory.glob("*.yaml")):
            with path.open(encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            if not isinstance(data, dict):
                raise SheetFormatError(f"{path.name}: expected a mapping")
            check_sheet_safety(data, origin=path.name)
            sheet = parse_sheet(data, origin=path.name)
            if sheet.id in self._sheets:
                raise SheetFormatError(f"{path.name}: duplicate sheet id {sheet.id!r}")
            if path.stem != sheet.id:
                raise SheetFormatError(f"{path.name}: file name must match id {sheet.id!r}")
            self._sheets[sheet.id] = sheet

    def get(self, sheet_id: str) -> PestSheet | None:
        return self._sheets.get(sheet_id)

    def list_for_crop(self, crop: Crop) -> list[PestSheet]:
        return [s for s in self._sheets.values() if crop in s.crops]

    def all(self) -> list[PestSheet]:
        return list(self._sheets.values())
