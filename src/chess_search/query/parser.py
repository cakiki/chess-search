from functools import reduce
from pathlib import Path

from lark import Lark, Transformer

from chess_search.query.expressions import (
    And,
    Anywhere,
    Empty,
    InCenter,
    IsolatedPawn,
    Material,
    Not,
    OnColor,
    OnFile,
    OnRank,
    OpenFile,
    Or,
    Phase,
    PieceOn,
    Rating,
    SideToMove,
    Tag,
)

GRAMMAR_PATH = Path(__file__).parent / "grammars" / "english.lark"

PIECE_MAP = {"rook": "R", "knight": "N", "bishop": "B", "queen": "Q", "king": "K", "pawn": "P", "piece": "RNBQKP"}
SQUARE_COLOR_MAP = {"light": "light", "dark": "dark", "white": "light", "black": "dark"}


def _any(nodes):
    return reduce(Or, nodes)


class QueryTransformer(Transformer):
    def piece(self, args):
        # args is either [color, piece] or [piece]
        symbols = PIECE_MAP[str(args[-1])]
        if len(args) == 1:
            return [*symbols, *symbols.lower()]  # [white, black]
        else:
            color = str(args[0])
            return [*symbols] if (color == "white") else [*symbols.lower()]

    def state(self, args):
        return Tag(str(args[0]))

    def on_file(self, args):
        return _any(OnFile(p, str(args[1])) for p in args[0])

    def on_rank(self, args):
        return _any(OnRank(p, int(args[1])) for p in args[0])

    def on_color(self, args):
        return _any(OnColor(p, SQUARE_COLOR_MAP[str(args[1])]) for p in args[0])

    def in_center(self, args):
        return _any(InCenter(p) for p in args[0])

    def anywhere(self, args):
        return _any(Anywhere(p) for p in args[0])

    def empty(self, args):
        return Empty(str(args[0]))

    def open_file(self, args):
        return OpenFile(str(args[0]))

    def phase(self, args):
        return Phase(str(args[0]))

    def piece_on(self, args):
        return _any(PieceOn(p, str(args[1])) for p in args[0])

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

    def side_to_move(self, args):
        return SideToMove("w" if str(args[0]) == "white" else "b")

    def can_castle(self, args):
        symbols = "KQ" if str(args[0]) == "white" else "kq"
        if len(args) > 1:
            symbols = symbols[0] if str(args[1]) == "kingside" else symbols[1]
        return _any(Tag(f"castling_{s}") for s in symbols)

    def material(self, args):
        n = int(args[1]) * (1 if str(args[0]) == "white" else -1)
        return Material(n, n)

    def material_equal(self, args):
        return Material(0, 0)

    def tag(self, args):
        return Tag(str(args[0]))

    def rating(self, args):
        return Rating(int(args[0]), int(args[1]))

    def isolated_pawn(self, args):
        symbols = "Pp" if len(args) == 1 else ("P" if str(args[0]) == "white" else "p")
        return _any(IsolatedPawn(p, str(args[-1])) for p in symbols)


parser = Lark(GRAMMAR_PATH.read_text(), parser="earley")


def parse(text):
    tree = parser.parse(text)
    return QueryTransformer().transform(tree)
