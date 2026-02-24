# mcp-memory

MCP server for persistent agent memory with semantic search

## Language

Python

## Build & Run Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy mcp_memory`

## Project Structure

- `mcp_memory/` - Main package source code
- `mcp_memory/main.py` - CLI entry point (click-based)
- `tests/` - Test files
- `pyproject.toml` - Project configuration and dependencies
