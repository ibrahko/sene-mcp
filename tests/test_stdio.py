"""Real transport: spawn the server as a subprocess and talk MCP over stdio,
exactly as Claude Desktop or MCP Inspector would."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters


def _params(tmp_path: Path) -> StdioServerParameters:
    # Use the installed `sene-mcp` entry point, as the README promises.
    scripts = Path(sys.executable).parent
    entry = shutil.which("sene-mcp", path=str(scripts)) or shutil.which("sene-mcp")
    assert entry, "the sene-mcp entry point is not installed"
    return StdioServerParameters(
        command=entry,
        args=[],
        env={"SENE_DATABASE_URL": f"sqlite:///{tmp_path / 'stdio.db'}"},
    )


async def test_server_answers_over_stdio(tmp_path: Path) -> None:
    async with Client(_params(tmp_path), read_timeout_seconds=30) as client:
        tools = await client.list_tools()
        assert {t.name for t in tools.tools} == {"get_market_price", "get_pest_sheet"}

        result = await client.call_tool("get_market_price", {"product": "rice", "market": "Mopti"})
        assert result.is_error is False
        data = json.loads(result.content[0].text)
        assert data["prices"][0]["town"] == "Mopti"


async def test_errors_reach_the_agent_as_tool_errors(tmp_path: Path) -> None:
    async with Client(_params(tmp_path), read_timeout_seconds=30) as client:
        result = await client.call_tool("get_pest_sheet", {"pest_sheet_id": "unknown"})
        assert result.is_error is True
        assert "NOT_FOUND" in result.content[0].text
