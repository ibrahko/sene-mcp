"""Domain entities. Pure Python: no framework, database or provider imports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Crop(StrEnum):
    """Crops covered by the pest knowledge base."""

    MAIZE = "maize"
    RICE = "rice"
    MILLET_SORGHUM = "millet_sorghum"


class Product(StrEnum):
    """Products traded on markets (millet and sorghum are priced separately)."""

    MAIZE = "maize"
    RICE = "rice"
    MILLET = "millet"
    SORGHUM = "sorghum"


class PestKind(StrEnum):
    INSECT = "insect"
    DISEASE = "disease"
    WEED = "weed"
    BIRD = "bird"
    OTHER = "other"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewStatus(StrEnum):
    SOURCED = "sourced"
    AGRONOMIST_REVIEWED = "agronomist_reviewed"


class DomainError(Exception):
    """An anticipated error with a stable code, safe to show to an agent."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Cooperative:
    id: int
    name: str
    region: str
    commune: str
    contact_phone: str


@dataclass(frozen=True)
class Market:
    id: int
    name: str
    town: str
    region: str


@dataclass(frozen=True)
class MarketPrice:
    market: Market
    product: Product
    price_fcfa_per_kg: int
    observed_on: date
    source: str
    is_demo_data: bool


@dataclass(frozen=True)
class Source:
    title: str
    publisher: str
    url: str
    consulted_on: date


@dataclass(frozen=True)
class PestNames:
    fr: str
    scientific: str
    bm: str | None = None


@dataclass(frozen=True)
class Management:
    prevention: tuple[str, ...] = ()
    cultural: tuple[str, ...] = ()
    biological: tuple[str, ...] = ()


@dataclass(frozen=True)
class PestSheet:
    id: str
    crops: tuple[Crop, ...]
    names: PestNames
    kind: PestKind
    symptoms: tuple[str, ...]
    keywords: tuple[str, ...]
    season: str
    severity: Severity
    management: Management
    treatment_guidance: str
    sources: tuple[Source, ...]
    review_status: ReviewStatus
