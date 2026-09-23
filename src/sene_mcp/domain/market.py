"""Market use cases."""

from __future__ import annotations

from sene_mcp.domain.models import DomainError, MarketPrice, Product
from sene_mcp.ports.repository import Repository


def parse_product(value: str) -> Product:
    try:
        return Product(value.strip().lower())
    except ValueError:
        known = ", ".join(p.value for p in Product)
        raise DomainError("UNKNOWN_PRODUCT", f"{value!r} is not covered. Known: {known}.") from None


def get_market_prices(
    repo: Repository, product: str, market: str | None = None
) -> list[MarketPrice]:
    """Latest price per market for a product; one market if `market` is given."""
    parsed = parse_product(product)
    market_id: int | None = None
    if market:
        found = repo.find_market(market)
        if found is None:
            known = ", ".join(m.name for m in repo.list_markets())
            raise DomainError(
                "UNKNOWN_MARKET", f"{market!r} is not a known market. Known: {known}."
            )
        market_id = found.id
    return repo.latest_prices(parsed, market_id)
