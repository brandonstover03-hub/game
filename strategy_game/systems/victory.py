"""Victory condition evaluation."""

from __future__ import annotations

from typing import Dict, Optional

from strategy_game.models.entities import Empire


def check_victory(empire: Empire, victory_cfg: Dict[str, float]) -> Optional[str]:
    if empire.treasury >= victory_cfg["economic_gold"]:
        return "Economic dominance"
    if len(empire.provinces) >= victory_cfg["military_provinces"]:
        return "Military conquest"
    if len(empire.technology) >= victory_cfg["technology_count"]:
        return "Technological supremacy"
    if empire.cultural_influence >= victory_cfg["cultural_influence"]:
        return "Cultural influence"
    if empire.diplomacy_score >= victory_cfg["diplomatic_score"]:
        return "Diplomatic victory"
    return None
