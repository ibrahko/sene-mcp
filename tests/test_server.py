"""End-to-end through the MCP layer, in process (no transport)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from sene_mcp.adapters.sql_repository import SqlRepository
from sene_mcp.adapters.yaml_knowledge import YamlKnowledgeBase
from sene_mcp.domain.safety import find_violations_in
from sene_mcp.server import build_server


@pytest.fixture
def server(repo: SqlRepository, kb: YamlKnowledgeBase) -> Any:
    return build_server(repo, kb)


def _payload(result: Any) -> dict[str, Any]:
    assert result.is_error is False
    data: dict[str, Any] = json.loads(result.content[0].text)
    return data


async def test_lists_the_lot_1_tools(server: Any) -> None:
    names = {t.name for t in await server.list_tools()}
    assert names == {"get_market_price", "get_pest_sheet"}


async def test_market_price_tool(server: Any) -> None:
    data = _payload(await server.call_tool("get_market_price", {"product": "maize"}))
    assert data["currency"] == "FCFA"
    assert data["is_demo_data"] is True
    assert len(data["prices"]) == 4


async def test_pest_sheet_tool(server: Any) -> None:
    data = _payload(
        await server.call_tool("get_pest_sheet", {"pest_sheet_id": "maize-fall-armyworm"})
    )
    assert data["scientific_name"] == "Spodoptera frugiperda"
    assert data["sources"]
    assert "service agricole" in data["treatment_guidance"]


async def test_domain_error_becomes_a_tool_error(server: Any) -> None:
    with pytest.raises(ToolError, match="NOT_FOUND"):
        await server.call_tool("get_pest_sheet", {"pest_sheet_id": "nope"})


async def test_every_call_is_logged(server: Any, repo: SqlRepository) -> None:
    await server.call_tool("get_market_price", {"product": "rice"})
    with pytest.raises(ToolError):
        await server.call_tool("get_market_price", {"product": "rice", "market": "Tombouctou"})
    assert repo.count_tool_calls() == 2


async def test_product_is_an_enum_in_the_input_schema(server: Any) -> None:
    tools = {t.name: t for t in await server.list_tools()}
    schema = json.dumps(tools["get_market_price"].input_schema)
    for product in ("maize", "rice", "millet", "sorghum"):
        assert f'"{product}"' in schema


async def test_unknown_product_returns_the_stable_code_and_is_logged(
    server: Any, repo: SqlRepository
) -> None:
    with pytest.raises(ToolError, match="UNKNOWN_PRODUCT"):
        await server.call_tool("get_market_price", {"product": "cotton"})
    assert repo.count_tool_calls() == 1


async def test_product_is_case_insensitive(server: Any) -> None:
    data = _payload(await server.call_tool("get_market_price", {"product": " RICE "}))
    assert data["product"] == "rice"


async def test_pest_sheet_id_is_case_insensitive(server: Any) -> None:
    data = _payload(
        await server.call_tool("get_pest_sheet", {"pest_sheet_id": " Maize-Fall-Armyworm "})
    )
    assert data["id"] == "maize-fall-armyworm"


async def test_no_tool_output_contains_forbidden_content(
    server: Any, kb: YamlKnowledgeBase
) -> None:
    for sheet in kb.all():
        data = _payload(await server.call_tool("get_pest_sheet", {"pest_sheet_id": sheet.id}))
        assert find_violations_in(data) == [], sheet.id
