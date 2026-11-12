import chess
import chess.pgn


def replay_moves(fen, moves):
    board = chess.Board(fen)
    positions = []
    for move in moves:
        board.push_uci(move)
        positions.append(board.copy())
    return positions


def puzzles(rows, puzzle_id: str = "PuzzleId", fen: str = "FEN", moves: str = "Moves", rating: str | None = "Rating", themes: str | None = "Themes"):
    for r in rows:
        tags = []
        if themes:
            tags += [f"theme_{t}" for t in r[themes]]
        if rating:
            tags.append(f"rating_{r[rating] // 100 * 100}")
        yield r[puzzle_id], replay_moves(r[fen], r[moves].split()), tags


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
