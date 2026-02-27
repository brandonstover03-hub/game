"""Economy system: production chains, taxes, trade, inflation, and upkeep."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from strategy_game.models.entities import Empire, Province
from strategy_game.systems.world import TERRAIN_OUTPUT


@dataclass
class MarketState:
    prices: Dict[str, float]


def default_market() -> MarketState:
    return MarketState(
        prices={
            "food": 1.0,
            "wood": 1.4,
            "stone": 1.6,
            "iron": 2.2,
            "advanced_goods": 3.5,
            "luxury": 4.3,
            "manpower": 2.0,
        }
    )


def produce_resources(empire: Empire, provinces: Dict[int, Province], buildings: Dict[str, Dict], season_mod: float, drag: float) -> Dict[str, float]:
    produced = {k: 0.0 for k in empire.resources}
    for pid in empire.provinces:
        p = provinces[pid]
        terrain_multi = TERRAIN_OUTPUT[p.terrain]
        stability_multi = max(0.55, p.stability / 100)
        infra_multi = 1 + (p.infrastructure - 1) * 0.08

        for b_key, spec in buildings.items():
            base_output = spec.get("base_output", {})
            inputs = spec.get("input", {})
            can_process = all(empire.resources.get(res, 0.0) >= amt for res, amt in inputs.items())
            if not can_process:
                continue

            for res, amt in inputs.items():
                empire.resources[res] -= amt

            for res, amt in base_output.items():
                node_scale = p.resource_nodes.get(res, 2) / 4
                terrain_scale = terrain_multi.get(res, 1.0)
                amount = amt * node_scale * terrain_scale * stability_multi * infra_multi * season_mod * (1 - drag)
                produced[res] = produced.get(res, 0.0) + amount

        produced["manpower"] += (p.population["peasants"] + p.population["workers"]) * 0.0025 * stability_multi

    for r, v in produced.items():
        empire.resources[r] = empire.resources.get(r, 0.0) + v
    return produced


def collect_taxes(empire: Empire, provinces: Dict[int, Province], base_tax_rate: float, tax_efficiency: float = 0.0) -> float:
    population = sum(sum(provinces[pid].population.values()) for pid in empire.provinces)
    effective_rate = base_tax_rate + tax_efficiency
    taxable_income = population * (0.05 + (empire.happiness / 100) * 0.03)
    taxes = taxable_income * effective_rate * (1 - empire.inflation)

    empire.treasury += taxes
    stability_penalty = max(0.0, (effective_rate - 0.2) * 25)
    empire.happiness = max(10, empire.happiness - stability_penalty * 0.2)
    empire.stability = max(10, empire.stability - stability_penalty * 0.35)
    return taxes


def apply_supply_demand(market: MarketState, empires: Iterable[Empire], elasticity: float) -> None:
    supply = {k: 0.0 for k in market.prices}
    demand = {k: 0.0 for k in market.prices}
    for empire in empires:
        for resource, price in market.prices.items():
            stock = empire.resources.get(resource, 0.0)
            supply[resource] += stock
            demand[resource] += max(40.0, 90.0 - stock * 0.3)

    for resource, price in market.prices.items():
        ratio = demand[resource] / max(1.0, supply[resource])
        adjustment = (ratio - 1) * elasticity
        market.prices[resource] = max(0.4, min(12.0, price * (1 + adjustment)))


def process_trade(empire: Empire, partner: Empire, market: MarketState) -> float:
    traded_value = 0.0
    for resource in ["food", "wood", "stone", "iron", "luxury", "advanced_goods"]:
        my_stock = empire.resources.get(resource, 0.0)
        partner_stock = partner.resources.get(resource, 0.0)
        if my_stock > 120 and partner_stock < 65:
            volume = min(20.0, my_stock - 110)
            empire.resources[resource] -= volume
            partner.resources[resource] += volume
            revenue = volume * market.prices.get(resource, 1.0)
            empire.treasury += revenue
            partner.treasury -= revenue * 0.8
            traded_value += revenue
    return traded_value


def apply_inflation_and_upkeep(empire: Empire, market: MarketState, military_upkeep: float, inflation_sensitivity: float) -> float:
    civil_upkeep = sum(empire.resources.get(r, 0.0) * 0.015 * market.prices.get(r, 1.0) for r in ["food", "wood", "stone", "iron"])
    total_upkeep = civil_upkeep + military_upkeep
    empire.treasury -= total_upkeep

    money_supply = empire.treasury + empire.resources.get("gold", 0.0) * market.prices.get("gold", 1.0)
    empire.inflation = min(0.35, max(0.0, empire.inflation + money_supply * inflation_sensitivity / 10000))
    return total_upkeep
