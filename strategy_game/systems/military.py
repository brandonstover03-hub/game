"""Military system and automatic battle resolver."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

from strategy_game.models.entities import Army, Empire, General, UnitStack
from strategy_game.systems.world import TERRAIN_OUTPUT


GENERAL_TRAITS = {
    "aggressive": {"attack": 0.08, "defense": -0.02, "morale": 2},
    "defensive": {"attack": -0.02, "defense": 0.08, "morale": 3},
    "logistician": {"supply": 0.12, "morale": 2},
    "defensive_commander": {"defense": 0.12, "morale": 4},
    "economic_planner": {},
}


@dataclass
class BattleReport:
    winner: str
    loser: str
    attacker_start: int
    defender_start: int
    attacker_remaining: int
    defender_remaining: int
    morale_swing: float
    turning_points: List[str]


def _army_power(army: Army, units: Dict[str, Dict], terrain: str, tech_bonus: Dict[str, float], variance: float, rng: random.Random) -> float:
    trait_bonus = GENERAL_TRAITS.get(army.general.trait, {})
    terrain_bonus = TERRAIN_OUTPUT[terrain]["combat"]
    supply_mod = 1 - max(0, (1 - army.supply) * 0.25)

    total = 0.0
    for stack in army.stacks:
        spec = units[stack.unit_key]
        base = (spec["attack"] * 1.2 + spec["defense"] + spec["health"] * 0.08) * stack.count
        morale_factor = (spec["morale"] + trait_bonus.get("morale", 0) + tech_bonus.get("morale", 0)) / 100
        terrain_factor = 1 + spec.get("terrain_modifiers", {}).get(terrain, 0.0) + terrain_bonus
        combat_factor = 1 + trait_bonus.get("attack", 0) + trait_bonus.get("defense", 0)
        tech_factor = 1 + tech_bonus.get("unit_attack", 0) + tech_bonus.get("unit_defense", 0)
        total += base * morale_factor * terrain_factor * combat_factor * tech_factor

    noise = rng.uniform(1 - variance, 1 + variance)
    return total * supply_mod * noise


def _counter_bonus(attacker: Army, defender: Army, units: Dict[str, Dict]) -> float:
    bonus = 1.0
    defender_categories = [units[s.unit_key]["category"] for s in defender.stacks]
    for stack in attacker.stacks:
        counters = units[stack.unit_key].get("counters", {})
        for cat in defender_categories:
            bonus += counters.get(cat, 0.0) * 0.2
    return bonus


def army_size(army: Army) -> int:
    return sum(stack.count for stack in army.stacks)


def military_upkeep(empire: Empire, units: Dict[str, Dict]) -> float:
    upkeep = 0.0
    for army in empire.armies:
        for stack in army.stacks:
            spec = units[stack.unit_key]
            upkeep += sum(spec.get("upkeep", {}).values()) * stack.count * 0.12
    return upkeep


def resolve_battle(attacker: Army, defender: Army, terrain: str, units: Dict[str, Dict], attacker_tech: Dict[str, float], defender_tech: Dict[str, float], random_variance: float, seed: int) -> BattleReport:
    rng = random.Random(seed)
    atk_start = army_size(attacker)
    def_start = army_size(defender)

    atk_power = _army_power(attacker, units, terrain, attacker_tech, random_variance, rng) * _counter_bonus(attacker, defender, units)
    def_power = _army_power(defender, units, terrain, defender_tech, random_variance, rng) * _counter_bonus(defender, attacker, units)

    if atk_power >= def_power:
        winner, loser = attacker.owner, defender.owner
        atk_loss_ratio = min(0.7, max(0.15, (def_power / max(1, atk_power)) * 0.45))
        def_loss_ratio = min(0.95, max(0.3, (atk_power / max(1, def_power)) * 0.7))
    else:
        winner, loser = defender.owner, attacker.owner
        atk_loss_ratio = min(0.95, max(0.35, (def_power / max(1, atk_power)) * 0.7))
        def_loss_ratio = min(0.7, max(0.15, (atk_power / max(1, def_power)) * 0.45))

    atk_remaining = max(0, int(atk_start * (1 - atk_loss_ratio)))
    def_remaining = max(0, int(def_start * (1 - def_loss_ratio)))
    morale_swing = (atk_power - def_power) / max(1, (atk_power + def_power)) * 20

    turning_points = [
        f"Terrain ({terrain}) shifted combat by {TERRAIN_OUTPUT[terrain]['combat']:+.2f}.",
        f"Counter interactions applied (attacker x{_counter_bonus(attacker, defender, units):.2f}, defender x{_counter_bonus(defender, attacker, units):.2f}).",
        f"Morale and commander effects produced a {morale_swing:+.2f} morale swing.",
    ]

    return BattleReport(
        winner=winner,
        loser=loser,
        attacker_start=atk_start,
        defender_start=def_start,
        attacker_remaining=atk_remaining,
        defender_remaining=def_remaining,
        morale_swing=morale_swing,
        turning_points=turning_points,
    )


def recruit_army(owner: str, province_id: int, trait: str = "aggressive") -> Army:
    stacks = [
        UnitStack("light_infantry", 12),
        UnitStack("heavy_infantry", 8),
        UnitStack("archers", 8),
        UnitStack("cavalry", 5),
        UnitStack("siege", 2),
    ]
    return Army(name=f"{owner} Legion", owner=owner, province_id=province_id, stacks=stacks, general=General(name="Auto", trait=trait))
