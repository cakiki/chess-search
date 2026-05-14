import chess


def position_to_tokens(board):
    piece_map = board.piece_map()
    tokens = [f"{piece.symbol()}_{chess.square_name(square)}" for square, piece in piece_map.items()]
    tokens.append("w" if board.turn else "b")
    from collections import Counter
    counts = Counter(piece.symbol() for piece in piece_map.values())
    for piece_type in "PNBRQKpnbrqk":
        tokens.append(f"{piece_type}_count_{counts.get(piece_type, 0)}")
    return tokens

def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions
