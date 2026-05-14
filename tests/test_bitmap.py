import chess
from chess_search.sparse.bitmap.index import BitmapIndex
from pyroaring import BitMap


def test_build_and_query():
    idx = BitmapIndex()
    b = chess.Board()
    idx.add(0, b)
    b.push_san("e4")
    idx.add(1, b)
    b.push_san("e5")
    idx.add(2, b)
    assert len(idx) == 48
    assert idx.query(["P_e4"]) == BitMap([1, 2])
    assert idx.query(["P_e4", "p_e5"]) == BitMap([2])


def test_merge():
    a, b = BitmapIndex(), BitmapIndex()
    board = chess.Board()
    a.add(0, board)
    board.push_san("e4")
    b.add(1, board)
    a |= b
    assert len(a) == 47
    assert a.query(["P_e2"]) == BitMap([0])
    assert a.query(["P_e4"]) == BitMap([1])


def test_empty_query():
    idx = BitmapIndex()
    assert idx.query(["N_z9"]) == BitMap()


def test_save_load(tmp_path):
    idx = BitmapIndex()
    b = chess.Board()
    idx.add(0, b)
    b.push_san("e4")
    idx.add(1, b)
    assert idx.query(["P_e4"]) == BitMap([1])
    assert idx.query(["P_e2"]) == BitMap([0])
    idx.save(str(tmp_path / "test_index"))
    loaded = BitmapIndex.load(str(tmp_path / "test_index"))
    assert len(loaded) == len(idx)
    assert loaded.query(["P_e4"]) == BitMap([1])
    assert loaded.query(["P_e2"]) == BitMap([0])


def test_add_source_and_resolve():
    idx = BitmapIndex()
    b = chess.Board()
    b.push_san("e4")
    boards_abc = [b.copy()]
    b.push_san("e5")
    boards_abc.append(b.copy())
    idx.add_source("abc", boards_abc)
    results = idx.query(["P_e4"])
    assert results == BitMap([0, 1])
    assert idx.resolve(results) == [("abc", 0), ("abc", 1)]


def test_merge_with_metadata():
    a = BitmapIndex()
    b_idx = BitmapIndex()
    board1 = chess.Board()
    board1.push_san("e4")
    a.add_source("puzzle_1", [board1.copy()])
    board2 = chess.Board()
    board2.push_san("d4")
    b_idx.add_source("puzzle_2", [board2.copy()])
    a |= b_idx
    assert a.resolve(a.query(["P_e4"])) == [("puzzle_1", 0)]
    assert a.resolve(a.query(["P_d4"])) == [("puzzle_2", 0)]
    assert a._next_id == 2


def test_fixture_roundtrip():
    import json
    from chess_search.utils import replay_moves, position_to_tokens

    with open("tests/fixtures/puzzles-sample.jsonl") as f:
        puzzles = [json.loads(line) for line in f]

    idx = BitmapIndex()
    all_boards = []
    for p in puzzles:
        boards = replay_moves(p["FEN"], p["Moves"].split())
        idx.add_source(p["PuzzleId"], boards)
        all_boards.extend(boards)

    for pos_id in [0, 100, 500, len(all_boards) - 1]:
        tokens = position_to_tokens(all_boards[pos_id])
        results = idx.query(tokens)
        assert pos_id in results

def test_pgn_indexing():
    import chess.pgn
    from chess_search.sparse.bitmap.query import on_file
    idx = BitmapIndex()
    with open("tests/fixtures/lichess_db_broadcast_2020-04.pgn") as f:
        while (game := chess.pgn.read_game(f)) is not None:
            boards = []
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                boards.append(board.copy())
            if boards:
                idx.add_source(game.headers.get("Site", ""), boards)
    assert len(idx) == 710
    assert idx._next_id == 7606
    assert len(on_file(idx, "R", "b")) == 557

def test_on_file():
    from chess_search.sparse.bitmap.query import on_file, anywhere

    idx = BitmapIndex()
    b = chess.Board()
    b.push_san("e4")
    idx.add(0, b)
    result = on_file(idx, "R", "a")
    assert 0 in result  # rook on a1
    result = on_file(idx, "R", "b")
    assert 0 not in result


def test_on_rank():
    from chess_search.sparse.bitmap.query import on_rank

    idx = BitmapIndex()
    b = chess.Board()
    idx.add(0, b)
    result = on_rank(idx, "P", 2)
    assert 0 in result  # white pawns on rank 2
    result = on_rank(idx, "P", 5)
    assert 0 not in result


def test_in_center():
    from chess_search.sparse.bitmap.query import in_center

    idx = BitmapIndex()
    b = chess.Board("8/8/8/3N4/4P3/8/8/8 w - - 0 1")  # N on d5, P on e4
    idx.add(0, b)
    assert 0 in in_center(idx, "P")
    assert 0 in in_center(idx, "N")
    b2 = chess.Board("8/8/8/8/8/5N2/4P3/8 w - - 0 1")  # N on f3, P on e2
    idx.add(1, b2)
    assert 1 not in in_center(idx, "P")
    assert 1 not in in_center(idx, "N")


def test_on_color():
    from chess_search.sparse.bitmap.query import on_color

    idx = BitmapIndex()
    b = chess.Board("8/8/8/8/8/3R4/8/2B5 w - - 0 1")  # B on c1 (dark), R on d3 (light)
    idx.add(0, b)
    assert 0 in on_color(idx, "B", "dark")
    assert 0 not in on_color(idx, "B", "light")
    assert 0 in on_color(idx, "R", "light")
    assert 0 not in on_color(idx, "R", "dark")

def test_empty_square():
    from chess_search.sparse.bitmap.query import empty_square
    idx = BitmapIndex()
    b1 = chess.Board("8/8/8/3N4/8/8/8/8 w - - 0 1")  # knight on d5 only
    b2 = chess.Board("8/8/8/3N4/4P3/8/8/8 w - - 0 1")  # knight on d5, pawn on e4
    idx.add(0, b1)
    idx.add(1, b2)
    result = empty_square(idx, "e4")
    assert 0 in result      # e4 is empty in position 0
    assert 1 not in result   # e4 is occupied in position 1

def test_side_to_move():
    idx = BitmapIndex()
    b = chess.Board()  # white to move
    idx.add(0, b)
    b.push_san("e4")   # now black to move
    idx.add(1, b)
    assert 0 in idx.query(["w"])
    assert 0 not in idx.query(["b"])
    assert 1 in idx.query(["b"])
    assert 1 not in idx.query(["w"])

def test_square_queries():
    from chess_search.sparse.bitmap.query import on_square, any_white_on, any_black_on, piece_on
    idx = BitmapIndex()
    b = chess.Board("8/8/8/3N4/8/8/8/3n4 w - - 0 1")  # white N on d5, black n on d1
    idx.add(0, b)
    assert 0 in on_square(idx, "d5")
    assert 0 not in on_square(idx, "e4")
    assert 0 in any_white_on(idx, "d5")
    assert 0 not in any_black_on(idx, "d5")
    assert 0 in any_black_on(idx, "d1")
    assert 0 in piece_on(idx, "N", "d5")
    assert 0 in piece_on(idx, "N", "d1")
    assert 0 not in piece_on(idx, "B", "d5")

def test_open_and_semi_open_file():
    from chess_search.sparse.bitmap.query import open_file, semi_open_file
    idx = BitmapIndex()
    b1 = chess.Board("8/8/8/8/8/8/8/8 w - - 0 1")          # empty board
    b2 = chess.Board("8/8/8/8/4P3/8/8/8 w - - 0 1")        # white pawn on e4
    b3 = chess.Board("8/4p3/8/8/4P3/8/8/8 w - - 0 1")      # both pawns on e file
    idx.add(0, b1)
    idx.add(1, b2)
    idx.add(2, b3)
    assert 0 in open_file(idx, "e")
    assert 1 not in open_file(idx, "e")
    assert 2 not in open_file(idx, "e")
    assert 1 in semi_open_file(idx, "e", "black")   # no black pawns, white pawn present
    assert 1 not in semi_open_file(idx, "e", "white")
    assert 2 not in semi_open_file(idx, "e", "white")

def test_flipcolor():
    from chess_search.sparse.bitmap.query import flipcolor
    assert flipcolor(["P_e4", "N_f3"]) == ["p_e4", "n_f3"]
    assert flipcolor(["p_e4", "n_f3"]) == ["P_e4", "N_f3"]


def test_mirror_vertical():
    from chess_search.sparse.bitmap.query import mirror_vertical
    assert mirror_vertical(["P_e4", "N_f3"]) == ["P_d4", "N_c3"]


def test_mirror_horizontal():
    from chess_search.sparse.bitmap.query import mirror_horizontal
    assert mirror_horizontal(["P_e4", "N_f3"]) == ["P_e5", "N_f6"]


def test_rotate_180():
    from chess_search.sparse.bitmap.query import rotate_180
    assert rotate_180(["P_e4"]) == ["P_d5"]


def test_flipcolor_with_index():
    from chess_search.sparse.bitmap.query import flipcolor
    idx = BitmapIndex()
    b1 = chess.Board("8/8/8/8/4P3/5N2/8/8 w - - 0 1")  # white P e4, N f3
    b2 = chess.Board("8/8/8/8/4p3/5n2/8/8 w - - 0 1")  # black p e4, n f3
    idx.add(0, b1)
    idx.add(1, b2)
    tokens = ["P_e4", "N_f3"]
    assert idx.query(tokens) == BitMap([0])
    assert idx.query(flipcolor(tokens)) == BitMap([1])

def test_piece_counts():
    idx = BitmapIndex()
    b = chess.Board("8/8/8/8/4P3/5N2/8/8 w - - 0 1")  # 1 white pawn, 1 white knight
    idx.add(0, b)
    assert 0 in idx.query(["P_count_1"])
    assert 0 in idx.query(["N_count_1"])
    assert 0 in idx.query(["Q_count_0"])
    assert 0 not in idx.query(["P_count_2"])
    