import chess


def position_to_tokens(board):
    return [f"{piece.symbol()}_{chess.square_name(square)}" for square, piece in board.piece_map().items()]


def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions
