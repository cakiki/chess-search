import chess

from chess_search.features import game_phase
from chess_search.features.nnue import DIM, halfkp

LONDON = chess.Board("rnb1kb1r/pp2pppp/1q3n2/2pp4/3P1B2/4PN2/PPP2PPP/RN1QKB1R w KQkq - 1 5")
MIDDLEGAME = chess.Board("r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2N1PN2/PPQ1BPPP/R4RK1 w - - 0 11")
ROOK_ENDGAME = chess.Board("8/8/4k3/8/8/8/8/R3K3 w Q - 0 1")


def test_game_phase():
    assert game_phase(chess.Board()) == "phase_opening"
    assert game_phase(LONDON) == "phase_opening"
    assert game_phase(MIDDLEGAME) == "phase_middlegame"
    assert game_phase(ROOK_ENDGAME) == "phase_endgame"


def test_halfkp():
    board = MIDDLEGAME
    assert len(halfkp(board)) == 52
    assert max(halfkp(board)) < 2 * DIM
    assert halfkp(board) == halfkp(board.mirror())
    assert halfkp(board, mirror=False) != halfkp(board.mirror(), mirror=False)

