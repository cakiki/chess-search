# /// script
# requires-python = ">=3.12"
# dependencies = ["chess", "torch", "numpy"]
# ///
"""Generate tests/fixtures/halfkp.json from nnue-pytorch's own HalfKP implementation.

Usage:
    git clone https://github.com/official-stockfish/nnue-pytorch /tmp/nnue-pytorch
    git -C /tmp/nnue-pytorch checkout ee27aba80f82709c3859783ed4434201b1ef02cf
    uv run scripts/halfkp_fixture.py /tmp/nnue-pytorch
"""

import json
import subprocess
import sys

import chess

sys.path.insert(0, f"{sys.argv[1]}/model")
from features.halfkp import NUM_PLANES, NUM_SQ, Features  # noqa: E402

FENS = [
    chess.STARTING_FEN,
    "rnb1kb1r/pp2pppp/1q3n2/2pp4/3P1B2/4PN2/PPP2PPP/RN1QKB1R w KQkq - 1 5",
    "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2N1PN2/PPQ1BPPP/R4RK1 w - - 0 11",
    "r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2N1PN2/PPQ1BPPP/R4RK1 b - - 0 11",
    "8/8/4k3/8/8/8/8/R3K3 w Q - 0 1",
    "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1",
]

features = Features()
cases = []
for fen in FENS:
    board = chess.Board(fen)
    white, black = features.get_active_features(board)
    first, second = (white, black) if board.turn else (black, white)
    indices = first.nonzero().flatten().tolist() + [int(i) + NUM_SQ * NUM_PLANES for i in second.nonzero().flatten()]
    cases.append({"fen": fen, "indices": indices})

commit = subprocess.check_output(["git", "-C", sys.argv[1], "rev-parse", "HEAD"], text=True).strip()
json.dump({"source": "official-stockfish/nnue-pytorch", "commit": commit, "cases": cases}, open("tests/fixtures/halfkp.json", "w"), indent=1)