from dataclasses import dataclass

from chess_search.indexes.bitmap.query import (
    anywhere,
    empty_square,
    in_center,
    isolated_pawn,
    on_color,
    on_file,
    on_rank,
    open_file,
)
from chess_search.indexes.bitmap.tokens import material_token


class Query:
    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)


@dataclass(frozen=True)
class Tag(Query):
    name: str


@dataclass(frozen=True)
class PieceOn(Query):
    piece: str
    square: str


@dataclass(frozen=True)
class OnFile(Query):
    piece: str
    file: str


@dataclass(frozen=True)
class OnRank(Query):
    piece: str
    rank: int


@dataclass(frozen=True)
class OnColor(Query):
    piece: str
    color: str


@dataclass(frozen=True)
class InCenter(Query):
    piece: str


@dataclass(frozen=True)
class Anywhere(Query):
    piece: str


@dataclass(frozen=True)
class Empty(Query):
    square: str


@dataclass(frozen=True)
class OpenFile(Query):
    file: str


@dataclass(frozen=True)
class Phase(Query):
    phase: str


@dataclass(frozen=True)
class And(Query):
    left: Query
    right: Query


@dataclass(frozen=True)
class Or(Query):
    left: Query
    right: Query


@dataclass(frozen=True)
class Not(Query):
    child: Query


@dataclass(frozen=True)
class SideToMove(Query):
    color: str


@dataclass(frozen=True)
class Material(Query):
    lo: int
    hi: int


@dataclass(frozen=True)
class Rating(Query):
    lo: int
    hi: int


@dataclass(frozen=True)
class IsolatedPawn(Query):
    piece: str
    file: str


def execute(expr, idx):
    match expr:
        case Tag(name):
            return idx.union([name])
        case PieceOn(piece, square):
            return idx.query([f"{piece}_{square}"])
        case OnFile(piece, file):
            return on_file(idx, piece, file)
        case OnRank(piece, rank):
            return on_rank(idx, piece, rank)
        case OnColor(piece, color):
            return on_color(idx, piece, color)
        case InCenter(piece):
            return in_center(idx, piece)
        case Anywhere(piece):
            return anywhere(idx, piece)
        case Empty(square):
            return empty_square(idx, square)
        case OpenFile(file):
            return open_file(idx, file)
        case Phase(phase):
            return idx.query([f"phase_{phase}"])
        case And(left, right):
            return execute(left, idx) & execute(right, idx)
        case Or(left, right):
            return execute(left, idx) | execute(right, idx)
        case Not(child):
            return idx._all_positions - execute(child, idx)
        case SideToMove(color):
            return idx.query([color])
        case Material(lo, hi):
            return idx.union([material_token(n) for n in range(lo, hi + 1)])
        case Rating(lo, hi):
            return idx.union([f"rating_{b}" for b in range(lo // 100 * 100, hi + 1, 100)])
        case IsolatedPawn(piece, file):
            return isolated_pawn(idx, piece, file)
        case _:
            raise ValueError(f"unknown expression: {expr}")
