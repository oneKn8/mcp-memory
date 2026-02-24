.PHONY: install test lint fmt typecheck clean

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

fmt:
	ruff format .

typecheck:
	mypy mcp_memory

clean:
	rm -rf dist/ build/ *.egg-info .mypy_cache .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
