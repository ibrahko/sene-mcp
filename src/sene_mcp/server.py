"""MCP server: declares the tools and wires them to the domain.

This layer stays thin: validate input, call the domain, shape the output, log the call.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from typing import Annotated, Literal, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field

from sene_mcp import __version__
from sene_mcp.adapters.sql_repository import SqlRepository
from sene_mcp.adapters.yaml_knowledge import YamlKnowledgeBase
from sene_mcp.config import load_settings
from sene_mcp.domain import market as market_domain
from sene_mcp.domain import pests as pests_domain
from sene_mcp.domain.models import DomainError
from sene_mcp.ports.knowledge import KnowledgeBase
from sene_mcp.ports.repository import Repository

INSTRUCTIONS = (
    "Tools for farming cooperatives in Mali: crop pest guidance and market prices. "
    "Pest sheets are hand-written from cited sources; never add a product name or a dose "
    "that is not in a sheet. Prices flagged is_demo_data are fictitious and must be "
    "presented as such."
)

T = TypeVar("T")
ProductName = Literal["maize", "rice", "millet", "sorghum"]


# ---------- Output schemas ----------


class PriceOut(BaseModel):
    market: str
    town: str
    region: str
    price_fcfa_per_kg: int
    observed_on: str = Field(description="ISO date of the observation")
    source: str


class MarketPriceResult(BaseModel):
    product: str
    currency: str = "FCFA"
    unit: str = "kg"
    prices: list[PriceOut]
    is_demo_data: bool = Field(description="True if any price is fictitious demo data")


class SourceOut(BaseModel):
    title: str
    publisher: str
    url: str
    consulted_on: str


class ManagementOut(BaseModel):
    prevention: list[str]
    cultural: list[str]
    biological: list[str]


class PestSheetResult(BaseModel):
    id: str
    name_fr: str
    name_bm: str | None
    scientific_name: str
    kind: str
    crops: list[str]
    symptoms: list[str]
    season: str
    severity: str
    management: ManagementOut
    treatment_guidance: str = Field(description="Fixed referral text: repeat it as is")
    sources: list[SourceOut]
    review_status: str = Field(description="'sourced' = not yet reviewed by an agronomist")
    is_demo_data: bool = False


# ---------- Server ----------


def build_server(repo: Repository, kb: KnowledgeBase) -> MCPServer:
    server = MCPServer("sene-mcp", instructions=INSTRUCTIONS, version=__version__)

    def run_logged(tool: str, summary: str, action: Callable[[], T]) -> T:
        started = time.perf_counter()
        status = "ok"
        try:
            return action()
        except DomainError as exc:
            status = exc.code
            raise ToolError(str(exc)) from exc
        except Exception:
            status = "crash"
            raise
        finally:
            elapsed = int((time.perf_counter() - started) * 1000)
            try:
                repo.log_tool_call(tool, summary, status, elapsed)
            except Exception as log_exc:  # logging must never break a tool call
                print(f"sene-mcp: could not log tool call: {log_exc}", file=sys.stderr)

    @server.tool()
    def get_market_price(
        product: Annotated[ProductName, Field(description="Crop product to price")],
        market: Annotated[
            str | None,
            Field(
                default=None,
                max_length=100,
                description='Market name or town, e.g. "Ségou". Omit to get all markets.',
            ),
        ] = None,
    ) -> MarketPriceResult:
        """Latest price per kg, in FCFA, of a crop product on Malian markets."""

        def action() -> MarketPriceResult:
            prices = market_domain.get_market_prices(repo, product, market)
            return MarketPriceResult(
                product=product.strip().lower(),
                prices=[
                    PriceOut(
                        market=p.market.name,
                        town=p.market.town,
                        region=p.market.region,
                        price_fcfa_per_kg=p.price_fcfa_per_kg,
                        observed_on=p.observed_on.isoformat(),
                        source=p.source,
                    )
                    for p in prices
                ],
                is_demo_data=any(p.is_demo_data for p in prices),
            )

        return run_logged("get_market_price", f"product={product} market={market}", action)

    @server.tool()
    def get_pest_sheet(
        pest_sheet_id: Annotated[
            str,
            Field(min_length=1, max_length=100, description='Sheet id, e.g. "maize-fall-armyworm"'),
        ],
    ) -> PestSheetResult:
        """Full pest sheet: symptoms, prevention and non-chemical control, sources.

        Treatments are never described: repeat `treatment_guidance` as is.
        """

        def action() -> PestSheetResult:
            sheet = pests_domain.get_pest_sheet(kb, pest_sheet_id)
            return PestSheetResult(
                id=sheet.id,
                name_fr=sheet.names.fr,
                name_bm=sheet.names.bm,
                scientific_name=sheet.names.scientific,
                kind=sheet.kind.value,
                crops=[c.value for c in sheet.crops],
                symptoms=list(sheet.symptoms),
                season=sheet.season,
                severity=sheet.severity.value,
                management=ManagementOut(
                    prevention=list(sheet.management.prevention),
                    cultural=list(sheet.management.cultural),
                    biological=list(sheet.management.biological),
                ),
                treatment_guidance=sheet.treatment_guidance,
                sources=[
                    SourceOut(
                        title=s.title,
                        publisher=s.publisher,
                        url=s.url,
                        consulted_on=s.consulted_on.isoformat(),
                    )
                    for s in sheet.sources
                ],
                review_status=sheet.review_status.value,
            )

        return run_logged("get_pest_sheet", f"id={pest_sheet_id}", action)

    return server


def main() -> None:
    """Entry point: `uv run sene-mcp` (stdio transport)."""
    from sene_mcp.seed import prepare_database

    settings = load_settings()
    print(f"sene-mcp: database {settings.database_url}", file=sys.stderr)
    engine = prepare_database(settings.database_url)
    server = build_server(SqlRepository(engine), YamlKnowledgeBase(settings.knowledge_dir))
    server.run("stdio")


if __name__ == "__main__":
    main()
