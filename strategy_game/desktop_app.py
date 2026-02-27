"""Standalone desktop app for the strategy simulation."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from strategy_game.game import advance_turn, initialize_game


class StrategyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Grand Strategy Simulator")
        self.geometry("980x680")

        self.game_state = None

        controls = ttk.Frame(self, padding=10)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Empire name:").pack(side=tk.LEFT)
        self.empire_name = tk.StringVar(value="Player Dominion")
        ttk.Entry(controls, textvariable=self.empire_name, width=26).pack(side=tk.LEFT, padx=(6, 16))

        ttk.Label(controls, text="Difficulty:").pack(side=tk.LEFT)
        self.difficulty = tk.StringVar(value="normal")
        ttk.Combobox(
            controls,
            textvariable=self.difficulty,
            values=["normal", "hard"],
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=(6, 16))

        ttk.Button(controls, text="New Game", command=self.start_game).pack(side=tk.LEFT)
        self.next_turn_button = ttk.Button(controls, text="Next Turn", command=self.next_turn, state=tk.DISABLED)
        self.next_turn_button.pack(side=tk.LEFT, padx=(8, 0))

        summary_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        summary_frame.pack(fill=tk.BOTH, expand=True)

        self.summary = tk.Text(summary_frame, wrap=tk.WORD)
        self.summary.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scroll = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary.yview)
        scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.summary.configure(yscrollcommand=scroll.set)

        self._write("Welcome! Click 'New Game' to start your standalone strategy campaign.")

    def _write(self, message: str) -> None:
        self.summary.insert(tk.END, f"{message}\n")
        self.summary.see(tk.END)

    def start_game(self) -> None:
        self.summary.delete("1.0", tk.END)
        name = self.empire_name.get().strip() or "Player Dominion"
        self.game_state = initialize_game(difficulty=self.difficulty.get(), player_name=name)
        player = self.game_state["player"]
        self.next_turn_button.configure(state=tk.NORMAL)
        self._write(f"New campaign started for {player.name}.")
        self._write(f"Owned provinces: {len(player.provinces)} | Starting treasury: {player.treasury:.1f}")
        self._write("Press 'Next Turn' to advance simulation.\n")

    def next_turn(self) -> None:
        if not self.game_state:
            self._write("Start a game first.")
            return

        summary = advance_turn(self.game_state)
        player = summary["player"]

        self._write(f"Turn {summary['turn']} ({summary['season'].title()})")
        self._write(
            f"Treasury: {player['treasury']:.1f} | Inflation: {player['inflation']:.2%} | "
            f"World inflation: {summary['world_inflation']:+.2%}"
        )
        self._write(
            f"Stability: {player['stability']:.1f} | Happiness: {player['happiness']:.1f} | "
            f"Provinces: {player['provinces']}"
        )

        if summary["events"]:
            self._write("Events:")
            for event in summary["events"]:
                self._write(f"  • {event}")

        battle = summary.get("battle")
        if battle:
            self._write(
                f"Battle: {battle['winner']} defeated {battle['loser']} "
                f"({battle['attacker_remaining']:.1f} vs {battle['defender_remaining']:.1f} strength remaining)"
            )

        if summary["victory"]:
            self._write(f"Victory achieved: {summary['victory']} on turn {summary['turn']}.")
            self.next_turn_button.configure(state=tk.DISABLED)

        self._write("")


def run() -> None:
    app = StrategyApp()
    app.mainloop()


if __name__ == "__main__":
    run()
