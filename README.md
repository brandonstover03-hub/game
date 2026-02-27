# Modular Grand Strategy Prototype

A scalable, data-driven single-player grand strategy simulation focused on economy, empire management, AI, and automatic military resolution.

## Language & Stack
- **Python 3** simulation core
- **Standalone desktop app** built with Tkinter (no browser required)
- Object-oriented modules with clean system separation
- Data-driven content via JSON (`strategy_game/data`)

## Folder Structure

```text
.
├── main.py
├── standalone_app.py
├── strategy_game/
│   ├── game.py
│   ├── desktop_app.py
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
- Inflation linked to **world market movement**: each empire inflation incorporates a global inflation signal from aggregate price changes.
- AI empire logic (economy-first growth, expansion, diplomacy posture, threat-based army growth).
- Auto-battle simulator with unit counters, terrain and tech modifiers, morale, commanders, supply effects, variance, and report output.
- Multiple victory conditions: economic, military, technological, cultural, diplomatic.
- Configurable difficulty and explicit balance tuning variables in config.
- Custom player empire naming in CLI and standalone desktop app.

## Run (CLI)

```bash
python main.py --turns 12 --difficulty normal --empire-name "My Empire"
```

## Run (Standalone App)

```bash
python standalone_app.py
```

## Optional: Build a downloadable executable
If you want to share without requiring Python:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed standalone_app.py --name grand-strategy
```

The built executable will appear under `dist/`.
