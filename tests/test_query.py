import chess
from pyroaring import BitMap

from chess_search.indexes.bitmap import BitmapIndex
from chess_search.query.expressions import (
    And,
    Anywhere,
    Empty,
    Material,
    Not,
    OnColor,
    OnFile,
    Or,
    Phase,
    PieceOn,
    SideToMove,
    Tag,
    execute,
)
from chess_search.query.parser import _any, parse


def test_parse_not():
    assert parse("no queen anywhere") == Not(Or(Anywhere("Q"), Anywhere("q")))
    assert parse("not empty e4") == Not(Empty("e4"))
    assert parse("not black to move") == Not(SideToMove("b"))


def test_parse_piece_colour():
    assert parse("white rook on b-file") == OnFile("R", "b")
    assert parse("black rook on b-file") == OnFile("r", "b")
    assert parse("rook on b-file") == Or(OnFile("R", "b"), OnFile("r", "b"))


def test_parse_newline_is_and():
    assert parse("white rook on b-file\nphase endgame") == And(OnFile("R", "b"), Phase("endgame"))


def test_parse_parentheses():
    assert parse("(empty e4 or empty d4)\nphase endgame") == And(Or(Empty("e4"), Empty("d4")), Phase("endgame"))


def test_execute_parsed_query():
    idx = BitmapIndex()
    idx.add(0, chess.Board("8/8/8/8/8/8/8/1R6 w - - 0 1"))
    idx.add(1, chess.Board("8/8/8/8/8/8/8/R7 w - - 0 1"))
    assert execute(parse("white rook on b-file"), idx) == BitMap([0])
    assert execute(parse("not white rook on b-file"), idx) == BitMap([1])


def test_execute_no_piece_on_dark_squares():
    idx = BitmapIndex()
    idx.add(0, chess.Board("8/8/8/8/8/8/8/1R6 w - - 0 1"))
    idx.add(1, chess.Board("8/8/8/8/8/8/8/R7 w - - 0 1"))
    assert execute(parse("no piece on dark squares"), idx) == BitMap([0])


def test_on_color():
    assert parse("bishop on white squares") == Or(OnColor("B", "light"), OnColor("b", "light"))
    assert parse("black bishop on dark squares") == OnColor("b", "dark")


def test_any_piece():
    assert parse("white piece on e4") == _any(PieceOn(p, "e4") for p in "RNBQKP")
    assert parse("piece on e4") == _any(PieceOn(p, "e4") for p in "RNBQKPrnbqkp")


def test_state():
    assert parse("checkmate") == Tag("checkmate")
    assert parse("no check") == Not(Tag("check"))
    idx = BitmapIndex()
    idx.add(0, chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"))
    idx.add(1, chess.Board())
    assert execute(parse("black to move\nno checkmate"), idx) == BitMap([])
    assert execute(parse("checkmate"), idx) == BitMap([0])


def test_can_castle():
    assert parse("white can castle") == Or(Tag("castling_K"), Tag("castling_Q"))
    assert parse("black can castle queenside") == Tag("castling_q")


def test_material():
    assert parse("white up 3") == Material(3, 3)
    assert parse("black up 1") == Material(-1, -1)
    assert parse("material equal") == Material(0, 0)
    idx = BitmapIndex()
    idx.add(0, chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"))
    idx.add(1, chess.Board())
    assert execute(parse("white up 9"), idx) == BitMap([0])
    assert execute(parse("material equal"), idx) == BitMap([1])
