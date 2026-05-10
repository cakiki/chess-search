import chess
from chess_search.sparse.bitmap import BitmapIndex
from pyroaring import BitMap


def test_build_and_query():
    idx = BitmapIndex()
    b = chess.Board()
    idx.add(0, b)
    b.push_san("e4")
    idx.add(1, b)
    b.push_san("e5")
    idx.add(2, b)
    assert len(idx) == 34
    assert idx.query(["P_e4"]) == BitMap([1, 2])
    assert idx.query(["P_e4", "p_e5"]) == BitMap([2])


def test_merge():
    a, b = BitmapIndex(), BitmapIndex()
    board = chess.Board()
    a.add(0, board)
    board.push_san("e4")
    b.add(1, board)
    a |= b
    assert len(a) == 33
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
