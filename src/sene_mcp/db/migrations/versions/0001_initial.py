"""Initial schema: cooperatives, markets, prices, offers, pest reports, tool call log.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cooperatives",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("commune", sa.String(100), nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=False),
    )
    op.create_table(
        "markets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("town", sa.String(100), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
    )
    op.create_table(
        "market_prices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("market_id", sa.Integer, sa.ForeignKey("markets.id"), nullable=False),
        sa.Column("product", sa.String(20), nullable=False),
        sa.Column("unit", sa.String(10), nullable=False),
        sa.Column("price_fcfa", sa.Integer, nullable=False),
        sa.Column("observed_on", sa.Date, nullable=False),
        sa.Column("source", sa.String(300), nullable=False),
        sa.Column("is_demo_data", sa.Boolean, nullable=False),
    )
    op.create_index("ix_market_prices_market_id", "market_prices", ["market_id"])
    op.create_index("ix_market_prices_product", "market_prices", ["product"])
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cooperative_id", sa.Integer, sa.ForeignKey("cooperatives.id"), nullable=False),
        sa.Column("product", sa.String(20), nullable=False),
        sa.Column("quantity_kg", sa.Integer, nullable=False),
        sa.Column("asking_price_fcfa", sa.Integer, nullable=False),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("client_ref", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("cooperative_id", "client_ref"),
    )
    op.create_index("ix_offers_cooperative_id", "offers", ["cooperative_id"])
    op.create_index("ix_offers_product", "offers", ["product"])
    op.create_table(
        "pest_reports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cooperative_id", sa.Integer, sa.ForeignKey("cooperatives.id"), nullable=False),
        sa.Column("zone", sa.String(100), nullable=False),
        sa.Column("crop", sa.String(20), nullable=False),
        sa.Column("pest_sheet_id", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pest_reports_cooperative_id", "pest_reports", ["cooperative_id"])
    op.create_index("ix_pest_reports_zone", "pest_reports", ["zone"])
    op.create_table(
        "tool_call_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tool", sa.String(50), nullable=False),
        sa.Column("input_summary", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tool_call_log_tool", "tool_call_log", ["tool"])


def downgrade() -> None:
    op.drop_table("tool_call_log")
    op.drop_table("pest_reports")
    op.drop_table("offers")
    op.drop_table("market_prices")
    op.drop_table("markets")
    op.drop_table("cooperatives")
