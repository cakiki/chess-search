from dataclasses import dataclass

class Query:
    def __and__(self, other): return And(self, other)
    def __or__(self, other): return Or(self, other)
    def __invert__(self): return Not(self)

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

from pyroaring import BitMap
from chess_search.sparse.bitmap.query import (
    on_file, on_rank, in_center, anywhere, empty_square, open_file
)

def execute(expr, idx):
    match expr:
        case PieceOn(piece, square):
            return idx.query([f"{piece}_{square}"])
        case OnFile(piece, file):
            return on_file(idx, piece, file)
        case OnRank(piece, rank):
            return on_rank(idx, piece, rank)
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
        case _:
            raise ValueError(f"unknown expression: {expr}")