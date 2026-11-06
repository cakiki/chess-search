import chess
import chess.pgn


def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions


def puzzles(rows):
    for r in rows:
        yield r["PuzzleId"], replay_moves(r["FEN"], r["Moves"].split())


def games(rows):
    for r in rows:
        boards = replay_moves(r.get("fen") or chess.STARTING_FEN, r["moves"])
        if boards:
            yield r["id"], boards


def pgn(file):
    while (game := chess.pgn.read_game(file)) is not None:
        yield {
            "id": game.headers.get("Site", ""),
            "fen": game.headers.get("FEN"),
            "moves": [m.uci() for m in game.mainline_moves()],
        }
