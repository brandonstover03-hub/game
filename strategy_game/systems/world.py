"""Procedural world map generation and world-level helpers."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from strategy_game.models.entities import Province


TERRAINS = ["plains", "forest", "hills", "mountains", "desert"]
TERRAIN_OUTPUT = {
    "plains": {"food": 1.2, "wood": 0.8, "movement": 1.0, "combat": 0.0},
    "forest": {"food": 0.9, "wood": 1.4, "movement": 0.8, "combat": 0.05},
    "hills": {"food": 0.9, "stone": 1.3, "iron": 1.1, "movement": 0.85, "combat": 0.08},
    "mountains": {"food": 0.6, "stone": 1.6, "iron": 1.4, "movement": 0.65, "combat": 0.12},
    "desert": {"food": 0.55, "luxury": 1.2, "movement": 0.9, "combat": -0.03},
}


@dataclass
class WorldMap:
    width: int
    height: int
    provinces: Dict[int, Province]

    def get_neighbors(self, province_id: int) -> List[int]:
        return self.provinces[province_id].neighbors


def _coord_to_id(x: int, y: int, width: int) -> int:
    return y * width + x


def _neighbors(x: int, y: int, width: int, height: int) -> List[Tuple[int, int]]:
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbors.append((nx, ny))
    return neighbors


def generate_world(width: int, height: int, seed: int) -> WorldMap:
    rng = random.Random(seed)
    provinces: Dict[int, Province] = {}

    for y in range(height):
        for x in range(width):
            pid = _coord_to_id(x, y, width)
            terrain = rng.choices(TERRAINS, weights=[34, 25, 20, 12, 9])[0]
            resource_nodes = {
                "food": rng.randint(2, 8),
                "wood": rng.randint(1, 8),
                "stone": rng.randint(1, 7),
                "iron": rng.randint(0, 6),
                "luxury": rng.randint(0, 4),
            }
            population = {
                "peasants": rng.randint(800, 1800),
                "workers": rng.randint(400, 1200),
                "nobles": rng.randint(50, 180),
                "soldiers": rng.randint(120, 360),
            }
            provinces[pid] = Province(
                id=pid,
                name=f"Province-{pid}",
                terrain=terrain,
                resource_nodes=resource_nodes,
                population=population,
                stability=rng.uniform(55, 80),
                infrastructure=rng.randint(1, 4),
                owner="Neutral",
            )

    for y in range(height):
        for x in range(width):
            pid = _coord_to_id(x, y, width)
            provinces[pid].neighbors = [_coord_to_id(nx, ny, width) for nx, ny in _neighbors(x, y, width, height)]

    return WorldMap(width=width, height=height, provinces=provinces)
