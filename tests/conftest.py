from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Engine

from sene_mcp.adapters.sql_repository import SqlRepository
from sene_mcp.adapters.yaml_knowledge import YamlKnowledgeBase
from sene_mcp.config import DEFAULT_KNOWLEDGE_DIR
from sene_mcp.seed import prepare_database


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Never touch the real per-user data folder during tests."""
    monkeypatch.setenv("SENE_DATA_DIR", str(tmp_path / "user-data"))


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = prepare_database(f"sqlite:///{tmp_path / 'test.db'}")
    yield engine
    engine.dispose()


@pytest.fixture
def repo(engine: Engine) -> SqlRepository:
    return SqlRepository(engine)


@pytest.fixture
def kb() -> YamlKnowledgeBase:
    return YamlKnowledgeBase(DEFAULT_KNOWLEDGE_DIR)
