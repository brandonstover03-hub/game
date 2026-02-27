"""Console-oriented strategy UI views with explainable tooltips."""

from __future__ import annotations

from strategy_game.models.entities import Empire
from strategy_game.systems.military import BattleReport


def province_panel(empire: Empire) -> str:
    return (
        f"Province Detail Panel | Empire={empire.name} | Provinces={len(empire.provinces)} | "
        "Tooltip: Terrain modifies production, movement, and combat outcomes."
    )


def economy_dashboard(empire: Empire) -> str:
    top = sorted(empire.resources.items(), key=lambda kv: kv[1], reverse=True)[:5]
    display = ", ".join(f"{k}:{v:.1f}" for k, v in top)
    return (
        f"Economy Dashboard | Treasury={empire.treasury:.1f} | Inflation={empire.inflation:.2%} | Top Resources -> {display}. "
        "Tooltip: Higher taxation increases revenue but reduces happiness/stability."
    )


def army_screen(empire: Empire) -> str:
    return (
        f"Army Screen | Armies={len(empire.armies)} | "
        "Tooltip: Supply lines reduce attrition and preserve morale in auto-battles."
    )


def diplomacy_screen(empire: Empire) -> str:
    return (
        f"Diplomacy Screen | Diplomatic Score={empire.diplomacy_score:.1f} | "
        "Tooltip: Trade agreements boost economy, alliances increase diplomatic victory progress."
    )


def battle_result_screen(report: BattleReport) -> str:
    points = " | ".join(report.turning_points)
    return (
        f"Battle Result | Winner={report.winner} | Loser={report.loser} | "
        f"Attacker {report.attacker_start}->{report.attacker_remaining}, Defender {report.defender_start}->{report.defender_remaining}. "
        f"Tooltip: Morale swing {report.morale_swing:+.2f}. Turning points: {points}"
    )
