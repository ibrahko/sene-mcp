"""Knowledge port: read-only access to validated pest sheets."""

from __future__ import annotations

from typing import Protocol

from sene_mcp.domain.models import Crop, PestSheet


class KnowledgeBase(Protocol):
    def get(self, sheet_id: str) -> PestSheet | None: ...

    def list_for_crop(self, crop: Crop) -> list[PestSheet]: ...

    def all(self) -> list[PestSheet]: ...
