"""AI empire planning for economy, expansion, and war choices."""

from __future__ import annotations

from typing import Dict, List

from strategy_game.models.entities import Empire, Province
from strategy_game.systems.diplomacy import DiplomacyState


def ai_choose_research(empire: Empire, tech_tree: Dict[str, Dict]) -> None:
    for tech_id, tech in tech_tree.items():
        if tech_id in empire.technology:
            continue
        if all(req in empire.technology for req in tech.get("requires", [])) and empire.research >= tech["cost"]:
            empire.research -= tech["cost"]
            empire.technology.append(tech_id)
            break


def ai_expand(empire: Empire, provinces: Dict[int, Province]) -> None:
    border_targets: List[int] = []
    for pid in empire.provinces:
        for n in provinces[pid].neighbors:
            if provinces[n].owner == "Neutral":
                border_targets.append(n)
    if border_targets and empire.stability > 45:
        target = sorted(border_targets, key=lambda p: sum(provinces[p].resource_nodes.values()), reverse=True)[0]
        provinces[target].owner = empire.name
        empire.provinces.append(target)
        empire.stability -= 1.2


def ai_decide_diplomacy(empire: Empire, others: List[Empire], diplo: DiplomacyState) -> None:
    for other in others:
        if other.name == empire.name:
            continue
        my_power = len(empire.provinces) + empire.treasury / 350
        their_power = len(other.provinces) + other.treasury / 350
        rel = diplo.get_relation(empire.name, other.name)

        if my_power > their_power * 1.35 and rel == "neutral":
            diplo.set_relation(empire.name, other.name, "war")
        elif my_power < their_power * 0.9 and rel in {"neutral", "war"}:
            diplo.set_relation(empire.name, other.name, "trade")


def ai_build_army_when_threatened(empire: Empire, threat_level: float) -> bool:
    if threat_level > 1.0 and empire.resources.get("manpower", 0) > 80 and empire.treasury > 350:
        empire.resources["manpower"] -= 80
        empire.treasury -= 280
        empire.stability += 0.8
        return True
    return False
