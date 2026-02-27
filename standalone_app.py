"""Launcher for the standalone desktop strategy app."""

from __future__ import annotations

import tkinter as tk

from strategy_game.desktop_app import run


if __name__ == "__main__":
    try:
        run()
    except tk.TclError as exc:
        raise SystemExit(
            "Unable to start desktop UI. A graphical display is required (missing $DISPLAY in headless environments)."
        ) from exc
