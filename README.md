# Modular Grand Strategy Prototype

A scalable, data-driven single-player grand strategy simulation focused on economy, empire management, AI, and automatic military resolution.

## Language & Stack
- **Python 3**
- Object-oriented modules with clean system separation
- Data-driven content via JSON (`strategy_game/data`)

## Folder Structure

```text
.
├── main.py
├── strategy_game/
│   ├── game.py
│   ├── models/
│   │   └── entities.py
│   ├── systems/
│   │   ├── ai.py
│   │   ├── diplomacy.py
│   │   ├── economy.py
│   │   ├── events.py
│   │   ├── military.py
│   │   ├── victory.py
│   │   └── world.py
│   ├── ui/
│   │   └── console.py
│   └── data/
│       ├── buildings.json
│       ├── config.json
│       ├── scenario.json
│       ├── tech_tree.json
│       └── units.json
└── START_HERE.md
```

## Implemented Deliverables
- Procedural province-based map generation with terrain/resource/population/stability/infrastructure.
- Deep economy simulation (production chains, classes, taxation, trade, prices, inflation, upkeep, seasonal output).
- AI empire logic (economy-first growth, expansion, diplomacy posture, threat-based army growth).
- Auto-battle simulator with unit counters, terrain and tech modifiers, morale, commanders, supply effects, variance, and report output.
- Multiple victory conditions: economic, military, technological, cultural, diplomatic.
- Configurable difficulty and explicit balance tuning variables in config.
- Example starting scenario loaded from JSON.
- Modular architecture that can be extended toward multiplayer networking in the future.

## Run

```bash
python main.py --turns 12 --difficulty normal
```

## UI Screens (Console Views)
- Province detail panel
- Economy dashboard
- Army management screen
- Diplomacy screen
- Battle result screen

All console views include tooltips explaining mechanics.
