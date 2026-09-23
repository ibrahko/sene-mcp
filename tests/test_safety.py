from __future__ import annotations

import pytest

from sene_mcp.domain.safety import TREATMENT_GUIDANCE, find_violations, is_safe


@pytest.mark.parametrize(
    "text",
    [
        "Pulvériser 2 g/l dans le cornet",
        "Appliquer 50 ml / ha au début",
        "1,5 kg par hectare suffit",
        "Respectez la dose indiquée",
        "Utilisez de l'émamectine benzoate",
        "Un traitement à la Cyperméthrine",
    ],
)
def test_forbidden_content_is_detected(text: str) -> None:
    assert find_violations(text)


@pytest.mark.parametrize(
    "text",
    [
        "Inspecter le champ chaque semaine dès la levée",
        "Semer 2 semaines plus tôt que d'habitude",
        "Prix : 230 FCFA/kg à Ségou",
        TREATMENT_GUIDANCE,
    ],
)
def test_ordinary_advice_is_allowed(text: str) -> None:
    assert is_safe(text)
