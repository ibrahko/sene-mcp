from __future__ import annotations

from sqlalchemy import Engine

from sene_mcp.seed import seed_demo_data


def test_seeding_twice_does_not_duplicate(engine: Engine) -> None:
    assert seed_demo_data(engine) is False
