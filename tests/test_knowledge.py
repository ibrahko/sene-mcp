"""These tests run on the real pest sheets: a bad sheet fails CI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from sene_mcp.adapters.yaml_knowledge import SheetFormatError, YamlKnowledgeBase, parse_sheet
from sene_mcp.config import DEFAULT_KNOWLEDGE_DIR
from sene_mcp.domain.models import Crop, PestSheet
from sene_mcp.domain.safety import TREATMENT_GUIDANCE, find_violations_in

SHEETS = YamlKnowledgeBase(DEFAULT_KNOWLEDGE_DIR).all()


SHEET_FILES = sorted(DEFAULT_KNOWLEDGE_DIR.glob("*.yaml"))


def _raw(name: str) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load((DEFAULT_KNOWLEDGE_DIR / name).read_text("utf-8"))
    return data


def test_knowledge_base_is_not_empty() -> None:
    assert len(SHEETS) >= 2


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_has_at_least_one_source(sheet: PestSheet) -> None:
    assert sheet.sources
    assert all(s.url.startswith(("http://", "https://")) for s in sheet.sources)


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_uses_the_fixed_treatment_guidance(sheet: PestSheet) -> None:
    assert sheet.treatment_guidance == TREATMENT_GUIDANCE


@pytest.mark.parametrize("path", SHEET_FILES, ids=lambda p: p.stem)
def test_no_field_of_the_raw_file_contains_a_product_or_dose(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.pop("treatment_guidance")
    assert find_violations_in(data) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("names.bm", "Emamectine benzoate 19 g/l"),
        ("sources.title", "Chlorpyrifos 480 g/l — dose 1 l/ha"),
        ("management.cultural", "Diluer 20 ml pour 15 litres d'eau"),
        ("season", "Traiter au Coragen"),
    ],
)
def test_loader_refuses_a_poisoned_sheet(tmp_path: Path, field: str, value: str) -> None:
    data = _raw("maize-fall-armyworm.yaml")
    if field == "names.bm":
        data["names"]["bm"] = value
    elif field == "sources.title":
        data["sources"][0]["title"] = value
    elif field == "management.cultural":
        data["management"]["cultural"].append(value)
    else:
        data[field] = value
    (tmp_path / "maize-fall-armyworm.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    with pytest.raises(SheetFormatError, match="forbidden content"):
        YamlKnowledgeBase(tmp_path)


def test_loader_refuses_a_custom_treatment_text(tmp_path: Path) -> None:
    data = _raw("maize-fall-armyworm.yaml")
    data["treatment_guidance"] = "Traitez vite."
    (tmp_path / "maize-fall-armyworm.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    with pytest.raises(SheetFormatError, match="treatment_guidance"):
        YamlKnowledgeBase(tmp_path)


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_has_symptoms_to_match_on(sheet: PestSheet) -> None:
    assert len(sheet.symptoms) >= 3


def test_every_crop_list_is_known() -> None:
    kb = YamlKnowledgeBase(DEFAULT_KNOWLEDGE_DIR)
    assert kb.list_for_crop(Crop.MAIZE)
    assert kb.list_for_crop(Crop.RICE)


def test_invalid_sheet_is_rejected() -> None:
    with pytest.raises(SheetFormatError):
        parse_sheet({"id": "broken", "crops": ["cassava"]})


def test_file_name_must_match_id(tmp_path: Path) -> None:
    data = _raw("maize-fall-armyworm.yaml")
    (tmp_path / "wrong-name.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    with pytest.raises(SheetFormatError, match="file name"):
        YamlKnowledgeBase(tmp_path)
