"""Create the schema and load demo data. Safe to run several times."""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.orm import Session

from sene_mcp.config import load_settings
from sene_mcp.db.migrate import upgrade_to_head
from sene_mcp.db.tables import CooperativeRow, MarketPriceRow, MarketRow

DEMO_DIR = Path(__file__).resolve().parent / "demo_data"


def _read(name: str) -> list[dict[str, str]]:
    with (DEMO_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def seed_demo_data(engine: Engine) -> bool:
    """Load demo rows if the database is empty. Returns True if rows were added."""
    with Session(engine) as session, session.begin():
        if session.scalar(select(func.count()).select_from(MarketRow)):
            return False
        for row in _read("markets.csv"):
            session.add(
                MarketRow(
                    id=int(row["id"]), name=row["name"], town=row["town"], region=row["region"]
                )
            )
        for row in _read("cooperatives.csv"):
            session.add(
                CooperativeRow(
                    id=int(row["id"]),
                    name=row["name"],
                    region=row["region"],
                    commune=row["commune"],
                    contact_phone=row["contact_phone"],
                )
            )
        session.flush()
        for row in _read("prices.csv"):
            session.add(
                MarketPriceRow(
                    id=int(row["id"]),
                    market_id=int(row["market_id"]),
                    product=row["product"],
                    unit=row["unit"],
                    price_fcfa=int(row["price_fcfa"]),
                    observed_on=date.fromisoformat(row["observed_on"]),
                    source=row["source"],
                    is_demo_data=row["is_demo_data"] == "true",
                )
            )
    return True


def prepare_database(database_url: str) -> Engine:
    """Migrate to the latest schema and load demo data on first run."""
    upgrade_to_head(database_url)
    engine = create_engine(database_url)
    if seed_demo_data(engine):
        print("sene-mcp: demo data loaded", file=sys.stderr)
    return engine


def main() -> None:
    settings = load_settings()
    prepare_database(settings.database_url)
    print(f"sene-mcp: database ready at {settings.database_url}", file=sys.stderr)
