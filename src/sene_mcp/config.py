"""Runtime settings, read from the environment (and an optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = Path.cwd() / "sene.db"
DEFAULT_KNOWLEDGE_DIR = PACKAGE_DIR / "knowledge" / "pests"


@dataclass(frozen=True)
class Settings:
    database_url: str
    knowledge_dir: Path
    anthropic_api_key: str | None


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        database_url=os.getenv("SENE_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}"),
        knowledge_dir=Path(os.getenv("SENE_KNOWLEDGE_DIR", str(DEFAULT_KNOWLEDGE_DIR))),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
    )
