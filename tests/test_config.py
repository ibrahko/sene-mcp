from __future__ import annotations

from pathlib import Path

import pytest

from sene_mcp.config import load_settings
from sene_mcp.seed import prepare_database


def test_database_location_does_not_depend_on_the_current_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SENE_DATABASE_URL", raising=False)
    monkeypatch.setenv("SENE_DATA_DIR", str(tmp_path / "data"))
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()
    monkeypatch.chdir(first)
    url_a = load_settings().database_url
    monkeypatch.chdir(second)
    assert load_settings().database_url == url_a
    assert str(tmp_path / "data") in url_a


def test_percent_sign_in_path_is_supported(tmp_path: Path) -> None:
    folder = tmp_path / "100%bio"
    folder.mkdir()
    engine = prepare_database(f"sqlite:///{folder / 'sene.db'}")
    engine.dispose()
    assert (folder / "sene.db").exists()
