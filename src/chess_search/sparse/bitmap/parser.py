from pathlib import Path
from lark import Lark, Transformer

from chess_search.sparse.bitmap.expressions import (
    And,
    Anywhere,
    Empty,
    InCenter,
    Not,
    OnFile,
    OnRank,
    OpenFile,
    Or,
    Phase,
    PieceOn,
    SideToMove,
)

GRAMMAR_PATH = Path(__file__).parent / "grammars" / "english.lark"

PIECE_MAP = {"rook": "R", "knight": "N", "bishop": "B", "queen": "Q", "king": "K", "pawn": "P"}


class QueryTransformer(Transformer):
    def piece(self, args):
        return PIECE_MAP[str(args[0])]

    def on_file(self, args):
        return OnFile(args[0], str(args[1]))

    def on_rank(self, args):
        return OnRank(args[0], int(args[1]))

    def in_center(self, args):
        return InCenter(args[0])

    def anywhere(self, args):
        return Anywhere(args[0])

    def empty(self, args):
        return Empty(str(args[0]))

    def open_file(self, args):
        return OpenFile(str(args[0]))

    def phase(self, args):
        return Phase(str(args[0]))

    def piece_on(self, args):
        return PieceOn(args[0], str(args[1]))

    def or_expr(self, args):
        return Or(args[0], args[1])
    
    def and_expr(self, args):
        return And(args[0], args[1])

    def not_expr(self, args):
        return Not(args[0])

    def line(self, args):
        return args[0]

    def start(self, args):
        result = args[0]
        for a in args[1:]:
            result = And(result, a)
        return result
    
    def white_to_move(self, args):
        return SideToMove("w")

    def black_to_move(self, args):
        return SideToMove("b")
    
parser = Lark(GRAMMAR_PATH.read_text(), parser="earley")


def parse(text):
    tree = parser.parse(text)
    return QueryTransformer().transform(tree)
