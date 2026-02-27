"""Random event system influenced by stability and expansion pressure."""

from __future__ import annotations

import random
from typing import Optional

from strategy_game.models.entities import Empire


def trigger_event(empire: Empire, turn: int, seed: int) -> Optional[str]:
    rng = random.Random(seed + turn + int(empire.stability))
    roll = rng.random()

    if empire.stability < 35 and roll < 0.3:
        loss = min(120.0, empire.treasury * 0.12)
        empire.treasury -= loss
        empire.happiness -= 4
        return f"Rebellion unrest in {empire.name}: treasury loss {loss:.1f}, happiness -4."

    if empire.stability > 70 and roll < 0.2:
        gain = 80 + rng.randint(0, 60)
        empire.treasury += gain
        empire.cultural_influence += 3
        return f"Festival success in {empire.name}: treasury +{gain}, cultural influence +3."

    if roll < 0.1:
        empire.research += 30
        return f"Scholar breakthrough in {empire.name}: research +30."

    return None
