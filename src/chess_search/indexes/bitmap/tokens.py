from collections import Counter

import chess

from chess_search.features import game_phase

_VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}


def position_to_tokens(board):
    piece_map = board.piece_map()
    tokens = [f"{piece.symbol()}_{chess.square_name(square)}" for square, piece in piece_map.items()]
    tokens.append("w" if board.turn else "b")
    counts = Counter(piece.symbol() for piece in piece_map.values())
    for piece_type in "PNBRQKpnbrqk":
        tokens.append(f"{piece_type}_count_{counts.get(piece_type, 0)}")
    tokens.append(game_phase(board))
    material = sum(_VALUES[s.upper()] * (n if s.isupper() else -n) for s, n in counts.items())
    material = max(-9, min(9, material))
    tokens.append(f"material_{material:+d}" if material else "material_0")
    for symbol, color, kingside in (
        ("K", chess.WHITE, True),
        ("Q", chess.WHITE, False),
        ("k", chess.BLACK, True),
        ("q", chess.BLACK, False),
    ):
        if (board.has_kingside_castling_rights if kingside else board.has_queenside_castling_rights)(color):
            tokens.append(f"castling_{symbol}")
    if board.is_check():
        tokens.append("check")
    if board.is_checkmate():
        tokens.append("checkmate")
    if board.is_stalemate():
        tokens.append("stalemate")
    return tokens


def material_token(n):
    return f"material_{n:+d}" if n else "material_0"
