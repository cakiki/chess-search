import chess

def position_to_tokens(board):
    tokens = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            tokens.append(f"{piece.symbol()}_{chess.square_name(square)}")
    return tokens

def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions
