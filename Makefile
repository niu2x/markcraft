.PHONY: run test coverage benchmark build

run:
	uv run python -m markcraft

test:
	uv run pytest

coverage:
	uv run coverage run -m pytest
	uv run coverage report

benchmark:
	uv run python tests/benchmark.py

build:
	uv build
