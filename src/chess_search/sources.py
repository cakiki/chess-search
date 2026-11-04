import chess


def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions

def puzzles(rows):
    pass

def games(rows):
    pass

def pgn(file):
    pass
