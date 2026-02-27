from argparse import ArgumentParser

from strategy_game.game import run_game


if __name__ == "__main__":
    parser = ArgumentParser(description="Grand strategy auto-battler simulation")
    parser.add_argument("--turns", type=int, default=12)
    parser.add_argument("--difficulty", choices=["normal", "hard"], default="normal")
    args = parser.parse_args()
    run_game(turns=args.turns, difficulty=args.difficulty)
