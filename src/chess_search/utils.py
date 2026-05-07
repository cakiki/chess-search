import chess

def position_to_tokens(board):
    tokens = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            tokens.append((piece.symbol(), chess.square_name(square)))
    return tokens