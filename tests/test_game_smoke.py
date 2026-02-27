from strategy_game.game import advance_turn, initialize_game


def test_initialize_game_applies_player_name() -> None:
    game = initialize_game(difficulty="normal", player_name="MergeFix Empire")
    assert game["player"].name == "MergeFix Empire"
    assert game["turn"] == 0


def test_advance_turn_produces_summary_and_inflation_signal() -> None:
    game = initialize_game(difficulty="normal", player_name="Verifier")
    summary = advance_turn(game)

    assert summary["turn"] == 1
    assert summary["player"]["name"] == "Verifier"
    assert "world_inflation" in summary
    assert isinstance(summary["world_inflation"], float)
    assert "inflation" in summary["player"]
