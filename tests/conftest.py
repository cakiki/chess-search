import json

import pytest


@pytest.fixture(scope="session")
def puzzle_rows():
    with open("tests/fixtures/puzzles-sample.jsonl") as f:
        return [json.loads(line) for line in f]
