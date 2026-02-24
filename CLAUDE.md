# mcp-memory

MCP server for persistent agent memory with semantic search.

## Language

Python (3.11+)

## Build & Run Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy mcp_memory`
- Run: `python -m mcp_memory.server`

## Project Structure

- `mcp_memory/server.py` - FastMCP server with tool definitions
- `mcp_memory/storage.py` - ChromaDB wrapper (MemoryStore class)
- `mcp_memory/config.py` - Environment variable configuration
- `mcp_memory/models.py` - Data models (Memory, RecallResult)
- `tests/` - pytest tests

## Architecture

- FastMCP 3.0 for MCP protocol (stdio transport)
- ChromaDB PersistentClient for vector storage (cosine similarity)
- One ChromaDB collection per project scope
- Default embedding model: all-MiniLM-L6-v2 (via sentence-transformers, auto-downloaded)
- Data stored at ~/.mcp-memory/ (configurable via MCP_MEMORY_DATA_DIR)

## MCP Tools

- `remember` - Store a memory with content, tags, project, importance
- `recall` - Semantic search across stored memories
- `forget` - Delete memories by ID, project, or tags
- `list_memories` - Browse memories with pagination and stats

## Conventions

- All tools return formatted strings
- Tags stored as comma-separated strings in ChromaDB metadata
- Per-project isolation via separate ChromaDB collections
