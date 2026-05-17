import chess


def position_to_tokens(board):
    piece_map = board.piece_map()
    tokens = [f"{piece.symbol()}_{chess.square_name(square)}" for square, piece in piece_map.items()]
    tokens.append("w" if board.turn else "b")
    from collections import Counter

    counts = Counter(piece.symbol() for piece in piece_map.values())
    for piece_type in "PNBRQKpnbrqk":
        tokens.append(f"{piece_type}_count_{counts.get(piece_type, 0)}")
    tokens.append(game_phase(board))
    return tokens


def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions


# https://github.com/lichess-org/scalachess/blob/master/core/src/main/scala/Divider.scala

_SCORE_TABLE = {
    (0, 0): lambda y: 0,
    (1, 0): lambda y: 1 + (8 - y),
    (2, 0): lambda y: 2 + (y - 2) if y > 2 else 0,
    (3, 0): lambda y: 3 + (y - 1) if y > 1 else 0,
    (4, 0): lambda y: 3 + (y - 1) if y > 1 else 0,
    (0, 1): lambda y: 1 + y,
    (1, 1): lambda y: 5 + abs(4 - y),
    (2, 1): lambda y: 4 + (y - 1),
    (3, 1): lambda y: 5 + (y - 1),
    (0, 2): lambda y: 2 + (6 - y) if y < 6 else 0,
    (1, 2): lambda y: 4 + (7 - y),
    (2, 2): lambda y: 7,
    (0, 3): lambda y: 3 + (7 - y) if y < 7 else 0,
    (1, 3): lambda y: 5 + (7 - y),
    (0, 4): lambda y: 3 + (7 - y) if y < 7 else 0,
}

_MIXEDNESS_REGIONS = [(0x0303 << (x + 8 * y), y + 1) for y in range(7) for x in range(7)]


def _majors_and_minors(board):
    return (board.occupied & ~(board.kings | board.pawns)).bit_count()


def _backrank_sparse(board):
    return (chess.BB_RANK_1 & board.occupied_co[chess.WHITE]).bit_count() < 4 or (
        chess.BB_RANK_8 & board.occupied_co[chess.BLACK]
    ).bit_count() < 4


def _mixedness(board):
    total = 0
    white = board.occupied_co[chess.WHITE]
    black = board.occupied_co[chess.BLACK]
    for region, y in _MIXEDNESS_REGIONS:
        w = (white & region).bit_count()
        b = (black & region).bit_count()
        total += _SCORE_TABLE.get((w, b), lambda y: 0)(y)
    return total


def game_phase(board):
    mm = _majors_and_minors(board)
    if mm <= 6:
        return "phase_endgame"
    if mm <= 10 or _backrank_sparse(board) or _mixedness(board) > 150:
        return "phase_middlegame"
    return "phase_opening"
