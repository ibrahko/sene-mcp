"""The domain must stay pure: no MCP, database, YAML or AI provider imports."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

DOMAIN = Path(__file__).resolve().parents[1] / "src" / "sene_mcp" / "domain"
ALLOWED_PREFIXES = ("sene_mcp.domain", "sene_mcp.ports", "__future__")
FORBIDDEN_ROOTS = {"mcp", "mcp_types", "sqlalchemy", "alembic", "yaml", "anthropic", "pydantic"}


@pytest.mark.parametrize("path", sorted(DOMAIN.glob("*.py")), ids=lambda p: p.name)
def test_domain_imports_only_the_standard_library_and_ports(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        for name in names:
            root = name.split(".")[0]
            assert root not in FORBIDDEN_ROOTS, f"{path.name} imports {name}"
            if root == "sene_mcp":
                assert name.startswith(ALLOWED_PREFIXES), f"{path.name} imports {name}"
