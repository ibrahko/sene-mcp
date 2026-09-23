"""SQLAlchemy implementation of the Repository port (SQLite in v0.1, PostgreSQL later)."""

from __future__ import annotations

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from sene_mcp.db.tables import MarketPriceRow, MarketRow, ToolCallLogRow
from sene_mcp.domain.models import Market, MarketPrice, Product
from sene_mcp.domain.text import fold, without_parentheses


def _market(row: MarketRow) -> Market:
    return Market(id=row.id, name=row.name, town=row.town, region=row.region)


class SqlRepository:
    def __init__(self, engine: Engine) -> None:
        self._sessions = sessionmaker(engine, expire_on_commit=False)

    def _session(self) -> Session:
        return self._sessions()

    def list_markets(self) -> list[Market]:
        with self._session() as session:
            rows = session.scalars(select(MarketRow).order_by(MarketRow.name))
            return [_market(r) for r in rows]

    def find_market(self, name: str) -> Market | None:
        """Match on the market name or its town, ignoring case and accents ("segou" = "Ségou")."""
        needle = fold(without_parentheses(name))
        for market in self.list_markets():
            if needle in (fold(without_parentheses(market.name)), fold(market.town)):
                return market
        return None

    def latest_prices(self, product: Product, market_id: int | None = None) -> list[MarketPrice]:
        with self._session() as session:
            latest = (
                select(
                    MarketPriceRow.market_id,
                    func.max(MarketPriceRow.observed_on).label("observed_on"),
                )
                .where(MarketPriceRow.product == product.value)
                .group_by(MarketPriceRow.market_id)
                .subquery()
            )
            query = (
                select(MarketPriceRow, MarketRow)
                .join(
                    latest,
                    (MarketPriceRow.market_id == latest.c.market_id)
                    & (MarketPriceRow.observed_on == latest.c.observed_on),
                )
                .join(MarketRow, MarketRow.id == MarketPriceRow.market_id)
                .where(MarketPriceRow.product == product.value)
                .order_by(MarketRow.name)
            )
            if market_id is not None:
                query = query.where(MarketPriceRow.market_id == market_id)
            return [
                MarketPrice(
                    market=_market(market),
                    product=product,
                    price_fcfa_per_kg=price.price_fcfa,
                    observed_on=price.observed_on,
                    source=price.source,
                    is_demo_data=price.is_demo_data,
                )
                for price, market in session.execute(query).all()
            ]

    def log_tool_call(self, tool: str, input_summary: str, status: str, duration_ms: int) -> None:
        with self._session() as session, session.begin():
            session.add(
                ToolCallLogRow(
                    tool=tool,
                    input_summary=input_summary[:500],
                    status=status[:50],
                    duration_ms=duration_ms,
                )
            )

    def count_tool_calls(self) -> int:
        with self._session() as session:
            return session.scalar(select(func.count()).select_from(ToolCallLogRow)) or 0
