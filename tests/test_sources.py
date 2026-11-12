import chess

from chess_search.sources import puzzles


def test_puzzles():
    row = {"PuzzleId": "x", "FEN": chess.STARTING_FEN, "Moves": "e2e4", "Rating": 1534, "Themes": ["fork", "endgame"]}
    assert next(puzzles([row]))[2] == ["theme_fork", "theme_endgame", "rating_1500"]
    assert next(puzzles([row], rating=None))[2] == ["theme_fork", "theme_endgame"]
