"""
HalfKP input features
Adapted from: https://github.com/official-stockfish/nnue-pytorch/blob/ee27aba80f82709c3859783ed4434201b1ef02cf/model/features/halfkp.py
Last point in the nnue-pytorch repo to have a halfkp implementation
Copyright (C) the nnue-pytorch authors, GPL-3.0
"""

import chess

NUM_SQ = 64
NUM_PT = 10
NUM_PLANES = NUM_SQ * NUM_PT + 1
DIM = NUM_PLANES * NUM_SQ


def orient(pov, square, mirror=True):
    return square ^ (0 if pov else 56 if mirror else 63)


def halfkp_index(pov, king_square, square, piece):
    plane = (piece.piece_type - 1) * 2 + (piece.color != pov)
    return 1 + square + plane * NUM_SQ + king_square * NUM_PLANES


def halfkp(board, mirror=True):
    halves = []
    for pov in (chess.WHITE, chess.BLACK):
        king = orient(pov, board.king(pov), mirror)
        pieces = ((sq, p) for sq, p in board.piece_map().items() if p.piece_type != chess.KING)
        halves.append(sorted(halfkp_index(pov, king, orient(pov, sq, mirror), p) for sq, p in pieces))
    first, second = halves if board.turn else halves[::-1]
    return first + [i + DIM for i in second]
