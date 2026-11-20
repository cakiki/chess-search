.PHONY: all lint fix format test grammar

all: fix format test

lint:
	ruff check src/ tests/ scripts/

fix:
	ruff check --fix src/ tests/ scripts/

format:
	ruff format src/ tests/ scripts/

test:
	pytest tests/

grammar:
	python -m chess_search.query.docs