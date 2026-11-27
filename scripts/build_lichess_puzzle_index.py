# /// script
# requires-python = ">=3.12"
# dependencies = ["chess-search[hf] @ git+https://github.com/cakiki/chess-search", "datasets"]
# ///
"""Build the Lichess puzzle index in parallel and push it to the Hub.

Usage:
    uv run scripts/build_lichess_puzzle_index.py christopher/chess-index --shards 4
"""

import argparse
from functools import partial

from datasets import load_dataset

from chess_search.indexes.bitmap import BitmapIndex
from chess_search.sources import puzzles

args = argparse.ArgumentParser()
args.add_argument("repo_id")
args.add_argument("--shards", type=int, default=4)
args = args.parse_args()

ds = load_dataset("Lichess/chess-puzzles", split="train").select_columns(["PuzzleId", "FEN", "Moves", "Rating", "Themes"])
idx = BitmapIndex.build_parallel([partial(puzzles, ds.shard(args.shards, i, contiguous=True)) for i in range(args.shards)])
idx.info()
idx.push_to_hub(args.repo_id)