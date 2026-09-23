"""SQLAlchemy tables. Amounts are integer FCFA, quantities integer kg, times UTC."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class CooperativeRow(Base):
    __tablename__ = "cooperatives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    region: Mapped[str] = mapped_column(String(100))
    commune: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(20))


class MarketRow(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    town: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100))


class MarketPriceRow(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)
    product: Mapped[str] = mapped_column(String(20), index=True)
    unit: Mapped[str] = mapped_column(String(10), default="kg")
    price_fcfa: Mapped[int] = mapped_column(Integer)
    observed_on: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(300))
    is_demo_data: Mapped[bool] = mapped_column(default=True)

    market: Mapped[MarketRow] = relationship()


class OfferRow(Base):
    __tablename__ = "offers"
    __table_args__ = (UniqueConstraint("cooperative_id", "client_ref"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cooperative_id: Mapped[int] = mapped_column(ForeignKey("cooperatives.id"), index=True)
    product: Mapped[str] = mapped_column(String(20), index=True)
    quantity_kg: Mapped[int] = mapped_column(Integer)
    asking_price_fcfa: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(10), default="open")
    client_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PestReportRow(Base):
    __tablename__ = "pest_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cooperative_id: Mapped[int] = mapped_column(ForeignKey("cooperatives.id"), index=True)
    zone: Mapped[str] = mapped_column(String(100), index=True)
    crop: Mapped[str] = mapped_column(String(20))
    pest_sheet_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ToolCallLogRow(Base):
    __tablename__ = "tool_call_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool: Mapped[str] = mapped_column(String(50), index=True)
    input_summary: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50))
    duration_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
