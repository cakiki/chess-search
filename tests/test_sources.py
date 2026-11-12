import chess

from chess_search.sources import games, puzzles


def test_pgn_indexing():
    from chess_search.indexes.bitmap.index import BitmapIndex
    from chess_search.indexes.bitmap.query import on_file
    from chess_search.sources import games, pgn

    with open("tests/fixtures/lichess_db_broadcast_2020-04.pgn") as f:
        idx = BitmapIndex.build_index(games(pgn(f)))
    assert len(idx) == 737
    assert idx._next_id == 7606
    assert len(on_file(idx, "R", "b")) == 557


def test_puzzles():
    row = {"PuzzleId": "x", "FEN": chess.STARTING_FEN, "Moves": "e2e4", "Rating": 1534, "Themes": ["fork", "endgame"]}
    assert next(puzzles([row]))[2] == ["theme_fork", "theme_endgame", "rating_1500"]
    assert next(puzzles([row], rating=None))[2] == ["theme_fork", "theme_endgame"]


def test_games():
    boards = next(games([{"id": "x", "fen": "8/8/8/3N4/8/8/8/8 w - - 0 1", "moves": ["d5f6"]}]))[1]
    assert boards[0].piece_at(chess.F6) == chess.Piece.from_symbol("N")
