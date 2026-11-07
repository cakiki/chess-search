import chess
from pyroaring import BitMap

from chess_search.indexes.bitmap import BitmapIndex
from chess_search.query.expressions import And, Anywhere, Empty, Not, OnFile, Or, Phase, SideToMove, execute
from chess_search.query.parser import parse


def test_not():
    assert parse("no queen anywhere") == Not(Or(Anywhere("Q"), Anywhere("q")))
    assert parse("not empty e4") == Not(Empty("e4"))
    assert parse("not black to move") == Not(SideToMove("b"))


def test_parse_piece_colour():
    assert parse("white rook on b-file") == OnFile("R", "b")
    assert parse("black rook on b-file") == OnFile("r", "b")
    assert parse("rook on b-file") == Or(OnFile("R", "b"), OnFile("r", "b"))


def test_parse_newline_is_and():
    assert parse("white rook on b-file\nphase endgame") == And(OnFile("R", "b"), Phase("endgame"))


def test_parse_not():
    assert parse("not empty e4") == Not(Empty("e4"))


def test_parse_parentheses():
    assert parse("(empty e4 or empty d4)\nphase endgame") == And(Or(Empty("e4"), Empty("d4")), Phase("endgame"))


def test_execute_parsed_query():
    idx = BitmapIndex()
    idx.add(0, chess.Board("8/8/8/8/8/8/8/1R6 w - - 0 1"))
    idx.add(1, chess.Board("8/8/8/8/8/8/8/R7 w - - 0 1"))
    assert execute(parse("white rook on b-file"), idx) == BitMap([0])
    assert execute(parse("not white rook on b-file"), idx) == BitMap([1])
