from __future__ import annotations

from datetime import date

import pytest

from sene_mcp.adapters.sql_repository import SqlRepository
from sene_mcp.domain.market import get_market_prices, parse_product
from sene_mcp.domain.models import DomainError, Product


def test_product_parsing_is_case_insensitive() -> None:
    assert parse_product(" Maize ") is Product.MAIZE


def test_unknown_product_has_a_stable_code() -> None:
    with pytest.raises(DomainError) as exc:
        parse_product("cotton")
    assert exc.value.code == "UNKNOWN_PRODUCT"


def test_returns_one_latest_price_per_market(repo: SqlRepository) -> None:
    prices = get_market_prices(repo, "maize")
    assert len(prices) == 4
    assert {p.observed_on for p in prices} == {date(2026, 9, 15)}


@pytest.mark.parametrize("town", ["Ségou", "segou", "SEGOU", " Ségou "])
def test_filters_by_town_ignoring_case_and_accents(repo: SqlRepository, town: str) -> None:
    prices = get_market_prices(repo, "rice", town)
    assert [p.market.town for p in prices] == ["Ségou"]


def test_demo_prices_are_flagged(repo: SqlRepository) -> None:
    assert all(p.is_demo_data for p in get_market_prices(repo, "millet"))


def test_unknown_market_lists_known_ones(repo: SqlRepository) -> None:
    with pytest.raises(DomainError) as exc:
        get_market_prices(repo, "maize", "Tombouctou")
    assert exc.value.code == "UNKNOWN_MARKET"
    assert "Bamako" in exc.value.message


def test_market_name_without_the_demo_label_matches(repo: SqlRepository) -> None:
    prices = get_market_prices(repo, "rice", "Marche de Mopti")
    assert [p.market.town for p in prices] == ["Mopti"]


def test_error_messages_do_not_echo_huge_inputs(repo: SqlRepository) -> None:
    with pytest.raises(DomainError) as exc:
        get_market_prices(repo, "maize", "x" * 5000)
    assert len(exc.value.message) < 400
