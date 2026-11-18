"""
HalfKP input features
Adapted from: https://github.com/official-stockfish/nnue-pytorch/blob/ee27aba80f82709c3859783ed4434201b1ef02cf/model/features/halfkp.py
Last point in the nnue-pytorch repo to have a halfkp implementation
Copyright (C) the nnue-pytorch
authors, GPL-3.0
"""

NUM_SQ = 64
NUM_PT = 10
NUM_PLANES = NUM_SQ * NUM_PT + 1


def orient(pov, square):
    return (63 * (not pov)) ^ square


def halfkp_index(pov, king_square, square, piece):
    plane = (piece.piece_type - 1) * 2 + (piece.color != pov)
    return 1 + orient(pov, square) + plane * NUM_SQ + king_square * NUM_PLANES
