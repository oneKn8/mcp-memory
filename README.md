# mcp-memory

MCP server for persistent agent memory with semantic search. Store decisions, context, and knowledge across sessions. Recall them with natural language queries.

## Features

- Semantic search via vector embeddings (ChromaDB + all-MiniLM-L6-v2)
- Per-project memory scoping
- Tag-based filtering
- Importance scoring (1-5)
- Pagination for browsing large memory stores
- Zero cloud dependencies -- runs entirely locally

## Installation

```bash
pip install -e .
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `MCP_MEMORY_DATA_DIR` | `~/.mcp-memory/` | Where memories are stored on disk |
| `MCP_MEMORY_DEFAULT_PROJECT` | `global` | Default project scope |
| `MCP_MEMORY_MAX_RESULTS` | `10` | Default number of recall results |

## MCP Client Setup

### Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-memory",
      "env": {
        "MCP_MEMORY_DATA_DIR": "~/.mcp-memory"
      }
    }
  }
}
```

### Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-memory"
    }
  }
}
```

## Tools

### remember

Store a memory for later recall.

| Arg | Type | Default | Description |
|---|---|---|---|
| `content` | string | required | The text to remember |
| `project` | string | "global" | Project scope |
| `tags` | list[string] | [] | Tags for filtering |
| `source` | string | "" | Where this memory came from |
| `importance` | int | 3 | Priority 1-5 |

### recall

Search memories by semantic similarity.

| Arg | Type | Default | Description |
|---|---|---|---|
| `query` | string | required | Natural language search |
| `project` | string | all | Limit to project |
| `tags` | list[string] | none | Filter by tags |
| `n_results` | int | 10 | Max results |
| `min_relevance` | float | none | Minimum relevance 0.0-1.0 |

### forget

Delete stored memories.

| Arg | Type | Default | Description |
|---|---|---|---|
| `memory_ids` | list[string] | none | Specific IDs to delete |
| `project` | string | none | Delete all in project |
| `tags` | list[string] | none | Delete by tags |

### list_memories

Browse stored memories with pagination.

| Arg | Type | Default | Description |
|---|---|---|---|
| `project` | string | all | Filter to project |
| `tags` | list[string] | none | Filter by tags |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page |

## Development

```bash
pip install -e ".[dev]"
pytest              # run tests
ruff check .        # lint
ruff format .       # format
mypy mcp_memory     # type check
```

## License

MIT
