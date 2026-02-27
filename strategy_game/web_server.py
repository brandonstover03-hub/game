"""Simple browser server exposing a 3D world view and turn API."""

from __future__ import annotations

import json
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from strategy_game.game import advance_turn, initialize_game


WEB_DIR = Path(__file__).resolve().parent.parent / "web"
SESSIONS = {}


def _serialize_state(state):
    world = state["world"]
    player = state["player"]
    provinces = []
    for p in world.provinces.values():
        provinces.append(
            {
                "id": p.id,
                "name": p.name,
                "terrain": p.terrain,
                "owner": p.owner,
                "stability": p.stability,
                "infrastructure": p.infrastructure,
                "resource_nodes": p.resource_nodes,
            }
        )

    return {
        "turn": state["turn"],
        "world_inflation": state["world_inflation"],
        "player": {
            "name": player.name,
            "treasury": player.treasury,
            "inflation": player.inflation,
            "stability": player.stability,
            "happiness": player.happiness,
            "provinces": len(player.provinces),
        },
        "provinces": provinces,
        "width": world.width,
        "height": world.height,
        "history": state["history"],
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, code=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_name):
        path = WEB_DIR / file_name
        if not path.exists():
            self.send_error(404)
            return
        content = path.read_bytes()
        ctype = "text/html" if file_name.endswith(".html") else "text/javascript" if file_name.endswith(".js") else "text/css"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            return self._serve_file("index.html")
        if parsed.path == "/app.js":
            return self._serve_file("app.js")
        if parsed.path == "/styles.css":
            return self._serve_file("styles.css")
        if parsed.path == "/api/state":
            qs = parse_qs(parsed.query)
            sid = qs.get("session", [""])[0]
            if sid not in SESSIONS:
                return self._json({"error": "session not found"}, 404)
            return self._json(_serialize_state(SESSIONS[sid]))
        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/new-game":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            name = payload.get("empire_name")
            difficulty = payload.get("difficulty", "normal")
            game = initialize_game(difficulty=difficulty, player_name=name)
            sid = str(uuid.uuid4())
            SESSIONS[sid] = game
            return self._json({"session": sid, "state": _serialize_state(game)})

        if self.path == "/api/next-turn":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            sid = payload.get("session")
            if sid not in SESSIONS:
                return self._json({"error": "session not found"}, 404)
            summary = advance_turn(SESSIONS[sid])
            return self._json({"summary": summary, "state": _serialize_state(SESSIONS[sid])})

        self.send_error(404)


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"3D browser client running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
