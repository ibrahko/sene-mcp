"""Runtime settings, read from the environment (and an optional .env file).

The database lives in a stable per-user folder, never in the current directory:
MCP clients such as Claude Desktop start the server from a folder we do not control.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from platformdirs import user_data_dir
from sqlalchemy import URL

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_KNOWLEDGE_DIR = PACKAGE_DIR / "knowledge" / "pests"


@dataclass(frozen=True)
class Settings:
    database_url: str
    knowledge_dir: Path
    anthropic_api_key: str | None


def default_data_dir() -> Path:
    """Windows: %LOCALAPPDATA%\\sene-mcp · macOS: ~/Library/Application Support/sene-mcp ·
    Linux: ~/.local/share/sene-mcp. Override with SENE_DATA_DIR."""
    override = os.getenv("SENE_DATA_DIR")
    return Path(override) if override else Path(user_data_dir("sene-mcp", appauthor=False))


def default_database_url() -> str:
    data_dir = default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return URL.create("sqlite", database=str(data_dir / "sene.db")).render_as_string()


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        database_url=os.getenv("SENE_DATABASE_URL") or default_database_url(),
        knowledge_dir=Path(os.getenv("SENE_KNOWLEDGE_DIR", str(DEFAULT_KNOWLEDGE_DIR))),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
    )
