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
    assert idx.query([("P", "e4")]) == BitMap([1, 2])
    assert idx.query([("P", "e4"), ("p", "e5")]) == BitMap([2])


def test_merge():
    a, b = BitmapIndex(), BitmapIndex()
    board = chess.Board()
    a.add(0, board)
    board.push_san("e4")
    b.add(1, board)
    a |= b
    assert len(a) == 33
    assert a.query([("P", "e2")]) == BitMap([0])
    assert a.query([("P", "e4")]) == BitMap([1])


def test_empty_query():
    idx = BitmapIndex()
    assert idx.query([("N", "z9")]) == BitMap()