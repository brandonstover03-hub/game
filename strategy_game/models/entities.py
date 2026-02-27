"""Core domain entities for the strategy simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


RESOURCES = ["food", "gold", "wood", "stone", "iron", "luxury", "manpower", "advanced_goods"]
POP_CLASSES = ["peasants", "workers", "nobles", "soldiers"]


@dataclass
class Province:
    id: int
    name: str
    terrain: str
    resource_nodes: Dict[str, int]
    population: Dict[str, int]
    stability: float
    infrastructure: int
    owner: str
    neighbors: List[int] = field(default_factory=list)


@dataclass
class General:
    name: str
    trait: str


@dataclass
class UnitStack:
    unit_key: str
    count: int


@dataclass
class Army:
    name: str
    owner: str
    province_id: int
    stacks: List[UnitStack]
    general: General
    supply: float = 1.0


@dataclass
class Empire:
    name: str
    is_player: bool
    treasury: float
    research: float
    stability: float
    happiness: float
    technology: List[str]
    policies: List[str]
    advisors: List[General]
    provinces: List[int] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=lambda: {r: 0.0 for r in RESOURCES})
    armies: List[Army] = field(default_factory=list)
    diplomacy_score: float = 0.0
    cultural_influence: float = 0.0
    inflation: float = 0.0

    def total_population(self, provinces: Dict[int, Province]) -> int:
        return sum(sum(provinces[p].population.values()) for p in self.provinces)
