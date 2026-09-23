from __future__ import annotations

import pytest

from sene_mcp.domain.safety import TREATMENT_GUIDANCE, find_violations, find_violations_in, is_safe


@pytest.mark.parametrize(
    "text",
    [
        # dosages, as written on the field
        "Pulvériser 2 g/l dans le cornet",
        "Appliquer 50 ml / ha au début",
        "1,5 kg par hectare suffit",
        "Diluer 20 ml pour 15 litres d'eau",
        "40 ml/15 l",
        "Mettre 1 sachet par pompe",
        "0,5 L/acre",
        "2 bouchons pour un pulvérisateur",
        "Respectez la dose indiquée",
        # active ingredients: French, English, accents, hyphens, spaces
        "Utilisez de l'émamectine benzoate",
        "Un traitement à la Cyperméthrine",
        "lambda cyhalothrine",
        "Lambda-cyhalothrin",
        "thiamethoxame",
        "2,4-D",
        # trade names
        "Le Coragen marche bien",
        "AMPLIGO",
    ],
)
def test_forbidden_content_is_detected(text: str) -> None:
    assert find_violations(text)


@pytest.mark.parametrize(
    "text",
    [
        "Inspecter le champ chaque semaine dès la levée",
        "Semer 2 semaines plus tôt que d'habitude",
        "Semer 2 lignes par ha",
        "Prix : 230 FCFA/kg à Ségou",
        "Préserver les ennemis naturels (fourmis, guêpes parasitoïdes)",
        "Désherber tôt, et deux fois",
        TREATMENT_GUIDANCE,
    ],
)
def test_ordinary_advice_is_allowed(text: str) -> None:
    assert is_safe(text)


def test_nested_structures_are_scanned_everywhere() -> None:
    data = {"names": {"bm": "ok"}, "sources": [{"title": "Chlorpyrifos 480 g/l"}]}
    violations = find_violations_in(data)
    assert violations
    assert all(v.startswith("sources[0].title") for v in violations)
