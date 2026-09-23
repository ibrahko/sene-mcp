"""These tests run on the real pest sheets: a bad sheet fails CI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from sene_mcp.adapters.yaml_knowledge import SheetFormatError, YamlKnowledgeBase, parse_sheet
from sene_mcp.config import DEFAULT_KNOWLEDGE_DIR
from sene_mcp.domain.models import Crop, PestSheet
from sene_mcp.domain.safety import TREATMENT_GUIDANCE, find_violations

SHEETS = YamlKnowledgeBase(DEFAULT_KNOWLEDGE_DIR).all()


def _all_text(sheet: PestSheet) -> str:
    parts = [sheet.names.fr, sheet.season, *sheet.symptoms, *sheet.keywords]
    parts += [*sheet.management.prevention, *sheet.management.cultural]
    parts += [*sheet.management.biological]
    return "\n".join(parts)


def test_knowledge_base_is_not_empty() -> None:
    assert len(SHEETS) >= 2


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_has_at_least_one_source(sheet: PestSheet) -> None:
    assert sheet.sources
    assert all(s.url.startswith(("http://", "https://")) for s in sheet.sources)


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_uses_the_fixed_treatment_guidance(sheet: PestSheet) -> None:
    assert sheet.treatment_guidance == TREATMENT_GUIDANCE


@pytest.mark.parametrize("sheet", SHEETS, ids=lambda s: s.id)
def test_sheet_contains_no_product_or_dose(sheet: PestSheet) -> None:
    assert find_violations(_all_text(sheet)) == []


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
    source = DEFAULT_KNOWLEDGE_DIR / "maize-fall-armyworm.yaml"
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    (tmp_path / "wrong-name.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(SheetFormatError, match="file name"):
        YamlKnowledgeBase(tmp_path)
