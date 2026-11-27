# /// script
# requires-python = ">=3.12"
# dependencies = ["datasets"]
# ///
"""Regenerate tests/fixtures/puzzles-sample.jsonl: the first 1000 Lichess puzzles."""

from datasets import load_dataset

ds = load_dataset("Lichess/chess-puzzles", split="train").select(range(1000))
ds.select_columns(["PuzzleId", "FEN", "Moves", "Rating", "Themes"]).to_json("tests/fixtures/puzzles-sample.jsonl")
