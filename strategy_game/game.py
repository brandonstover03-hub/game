"""Core game loop wiring world, economy, AI, diplomacy, and military systems."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from strategy_game.models.entities import Army, Empire, General, UnitStack
from strategy_game.systems import ai, diplomacy, economy, events, military, victory, world
from strategy_game.ui import console


DATA_DIR = Path(__file__).parent / "data"
SEASONS = ["spring", "summer", "autumn", "winter"]


def load_json(name: str) -> Dict:
    with (DATA_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _tech_bonus(empire: Empire, tech_tree: Dict[str, Dict]) -> Dict[str, float]:
    bonus: Dict[str, float] = {}
    for tid in empire.technology:
        for k, v in tech_tree.get(tid, {}).get("effects", {}).items():
            bonus[k] = bonus.get(k, 0.0) + v
    return bonus


def _build_player_army(name: str, province_id: int) -> Army:
    return Army(
        name=f"{name} Vanguard",
        owner=name,
        province_id=province_id,
        general=General(name="Marshal Ilya", trait="defensive"),
        stacks=[
            UnitStack("light_infantry", 16),
            UnitStack("heavy_infantry", 10),
            UnitStack("archers", 10),
            UnitStack("cavalry", 6),
            UnitStack("siege", 3),
            UnitStack("elite_guard", 4),
        ],
        supply=1.0,
    )


def initialize_game(difficulty: str = "normal"):
    config = load_json("config.json")
    buildings = load_json("buildings.json")
    units = load_json("units.json")
    tech_tree = load_json("tech_tree.json")
    scenario = load_json("scenario.json")

    w = config["world"]
    world_map = world.generate_world(w["width"], w["height"], w["seed"])

    p_cfg = scenario["player_empire"]
    player = Empire(
        name=p_cfg["name"],
        is_player=True,
        treasury=p_cfg["treasury"],
        research=p_cfg["research"],
        stability=p_cfg["stability"],
        happiness=p_cfg["happiness"],
        technology=p_cfg["technology"],
        policies=p_cfg["policies"],
        advisors=[General(name=a["name"], trait=a["trait"]) for a in p_cfg["advisors"]],
    )

    ai_empires: List[Empire] = []
    for idx, a in enumerate(scenario["ai_empires"], start=1):
        ai_empires.append(
            Empire(
                name=a["name"],
                is_player=False,
                treasury=a["treasury"],
                research=0,
                stability=a["stability"],
                happiness=55,
                technology=[],
                policies=[a["personality"]],
                advisors=[General(name=f"AI-{idx}", trait="aggressive")],
            )
        )

    empire_cycle = [player] + ai_empires
    province_ids = list(world_map.provinces.keys())
    for i, pid in enumerate(province_ids):
        owner = empire_cycle[i % len(empire_cycle)]
        world_map.provinces[pid].owner = owner.name
        owner.provinces.append(pid)

    player.armies.append(_build_player_army(player.name, player.provinces[0]))
    for idx, empire in enumerate(ai_empires, start=1):
        empire.armies.append(
            Army(
                name=f"{empire.name} Host",
                owner=empire.name,
                province_id=empire.provinces[0],
                stacks=[UnitStack("light_infantry", 12), UnitStack("archers", 8), UnitStack("cavalry", 4)],
                general=General(name=f"General-{idx}", trait="aggressive"),
                supply=0.9,
            )
        )

    diplo = diplomacy.DiplomacyState()
    for i in range(len(empire_cycle)):
        for j in range(i + 1, len(empire_cycle)):
            diplo.set_relation(empire_cycle[i].name, empire_cycle[j].name, "trade")

    return {
        "config": config,
        "difficulty": config["difficulty"][difficulty],
        "world": world_map,
        "buildings": buildings,
        "units": units,
        "tech_tree": tech_tree,
        "player": player,
        "ai_empires": ai_empires,
        "diplomacy": diplo,
        "market": economy.default_market(),
    }


def run_game(turns: int = 12, difficulty: str = "normal") -> None:
    g = initialize_game(difficulty)
    cfg = g["config"]
    balance = cfg["balance"]

    empires = [g["player"], *g["ai_empires"]]
    for turn in range(1, turns + 1):
        season = SEASONS[(turn - 1) % 4]
        season_mod = balance["season_modifiers"][season]
        drag = max(0.0, (turn - balance["late_game_drag_start_turn"])) * balance["late_game_drag_per_turn"]

        for empire in empires:
            tech_bonus = _tech_bonus(empire, g["tech_tree"])
            produced = economy.produce_resources(empire, g["world"].provinces, g["buildings"], season_mod, drag)
            taxes = economy.collect_taxes(empire, g["world"].provinces, balance["base_tax_rate"], tech_bonus.get("tax_efficiency", 0.0))

            empire.research += 35 + len(empire.provinces) * 2
            if not empire.is_player:
                empire.research *= 1 + g["difficulty"]["ai_economy_bonus"]
                ai.ai_choose_research(empire, g["tech_tree"])
                ai.ai_expand(empire, g["world"].provinces)
                threat = sum(1 for rel in g["diplomacy"].relations.values() if rel == "war")
                if ai.ai_build_army_when_threatened(empire, threat):
                    empire.armies.append(
                        Army(
                            name=f"{empire.name} Reserve",
                            owner=empire.name,
                            province_id=empire.provinces[0],
                            stacks=[UnitStack("heavy_infantry", 8), UnitStack("archers", 6)],
                            general=General(name="Reserve", trait="defensive"),
                            supply=0.95,
                        )
                    )

            upk = military.military_upkeep(empire, g["units"])
            economy.apply_inflation_and_upkeep(empire, g["market"], upk, balance["inflation_sensitivity"])
            event_msg = events.trigger_event(empire, turn, seed=cfg["world"]["seed"])

            if empire.is_player:
                print(f"\nTURN {turn} ({season.upper()}) - {empire.name}")
                print(console.province_panel(empire))
                print(console.economy_dashboard(empire))
                print(console.army_screen(empire))
                if event_msg:
                    print(f"Event: {event_msg}")
                print(f"Turn production sample: food +{produced.get('food', 0):.1f}, iron +{produced.get('iron', 0):.1f}, taxes +{taxes:.1f}")

        economy.apply_supply_demand(g["market"], empires, balance["trade_price_elasticity"])
        economy.process_trade(g["player"], g["ai_empires"][0], g["market"])

        for ai_empire in g["ai_empires"]:
            ai.ai_decide_diplomacy(ai_empire, empires, g["diplomacy"])
        for e in empires:
            diplomacy.evaluate_diplomatic_score(e, g["diplomacy"])

        if g["player"].armies and g["ai_empires"][0].armies and turn % 3 == 0:
            a1 = g["player"].armies[0]
            a2 = g["ai_empires"][0].armies[0]
            terrain = g["world"].provinces[a1.province_id].terrain
            report = military.resolve_battle(
                a1,
                a2,
                terrain,
                g["units"],
                _tech_bonus(g["player"], g["tech_tree"]),
                _tech_bonus(g["ai_empires"][0], g["tech_tree"]),
                balance["battle_random_variance"],
                cfg["world"]["seed"] + turn,
            )
            print(console.battle_result_screen(report))

        print(console.diplomacy_screen(g["player"]))
        won = victory.check_victory(g["player"], cfg["victory"])
        if won:
            print(f"\nVictory achieved: {won} on turn {turn}.")
            return

    print("\nSimulation ended without a decisive victory. Continue expanding systems or increase turn count.")
