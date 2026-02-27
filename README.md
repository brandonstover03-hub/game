# Modular Grand Strategy Prototype

A scalable, data-driven single-player grand strategy simulation focused on economy, empire management, AI, and automatic military resolution.

## Language & Stack
- **Python 3** backend simulation
- **Browser client** with **Three.js** for a 3D world view
- Object-oriented modules with clean system separation
- Data-driven content via JSON (`strategy_game/data`)

## Folder Structure

```text
.
├── main.py
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── strategy_game/
│   ├── game.py
│   ├── web_server.py
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
- Inflation linked to **world market movement**: each empire inflation now incorporates a global inflation signal from aggregate price changes.
- AI empire logic (economy-first growth, expansion, diplomacy posture, threat-based army growth).
- Auto-battle simulator with unit counters, terrain and tech modifiers, morale, commanders, supply effects, variance, and report output.
- Multiple victory conditions: economic, military, technological, cultural, diplomatic.
- Configurable difficulty and explicit balance tuning variables in config.
- Custom player empire naming in CLI and browser new-game flow.
- Browser 3D map visualization for provinces (Three.js), with turn progression via API.

## Run (CLI)

```bash
python main.py --turns 12 --difficulty normal --empire-name "My Empire"
```

## Run (Browser + 3D)

```bash
python -m strategy_game.web_server
```

Open `http://127.0.0.1:8000` and create a game with your chosen empire name.
