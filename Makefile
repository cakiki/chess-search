.PHONY: all lint fix format test

all: fix format test

lint:
	ruff check src/ tests/

fix:
	ruff check --fix src/ tests/

format:
	ruff format src/ tests/

test:
	pytest tests/
