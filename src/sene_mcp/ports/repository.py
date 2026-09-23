"""Storage port: what the domain needs from a database, nothing more."""

from __future__ import annotations

from typing import Protocol

from sene_mcp.domain.models import Market, MarketPrice, Product


class Repository(Protocol):
    def list_markets(self) -> list[Market]: ...

    def find_market(self, name: str) -> Market | None: ...

    def latest_prices(self, product: Product, market_id: int | None = None) -> list[MarketPrice]:
        """Most recent price per market for `product`, optionally for one market."""
        ...

    def log_tool_call(
        self, tool: str, input_summary: str, status: str, duration_ms: int
    ) -> None: ...
