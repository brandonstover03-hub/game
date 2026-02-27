"""Diplomatic state and interaction scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from strategy_game.models.entities import Empire


@dataclass
class DiplomacyState:
    relations: Dict[Tuple[str, str], str] = field(default_factory=dict)

    def set_relation(self, a: str, b: str, relation: str) -> None:
        key = tuple(sorted((a, b)))
        self.relations[key] = relation

    def get_relation(self, a: str, b: str) -> str:
        return self.relations.get(tuple(sorted((a, b))), "neutral")


def evaluate_diplomatic_score(empire: Empire, state: DiplomacyState) -> float:
    score = 0.0
    for (a, b), relation in state.relations.items():
        if empire.name not in (a, b):
            continue
        if relation == "alliance":
            score += 18
        elif relation == "trade":
            score += 10
        elif relation == "vassal":
            score += 15
        elif relation == "war":
            score -= 10
    empire.diplomacy_score = score + max(0, empire.stability - 50) * 0.3
    return empire.diplomacy_score
