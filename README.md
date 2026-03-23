# mcp-memory

**Your AI agent forgets everything between sessions. This fixes that.**

An MCP server that gives any AI agent persistent memory with semantic search. Store decisions, context, and knowledge once -- recall them with natural language queries across any future session.

Built on ChromaDB embeddings, scoped per project, runs entirely locally.

## Why

Every MCP-based agent (Claude Desktop, Claude Code, Cursor) starts each session with amnesia. Decisions made yesterday are gone. Context from last week is gone. You re-explain the same things every time.

mcp-memory adds four tools -- `remember`, `recall`, `forget`, `list_memories` -- that persist knowledge across sessions with vector similarity search. Your agent remembers what matters and finds it when relevant.

## Features

- **Semantic recall** -- vector embeddings (all-MiniLM-L6-v2) find related memories, not just keyword matches
- **Per-project scoping** -- memories don't leak between projects
- **Importance scoring** -- prioritize critical decisions (1-5 scale)
- **Tag-based filtering** -- organize memories by category
- **Fully local** -- ChromaDB on disk, no cloud, no API keys, no telemetry

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
