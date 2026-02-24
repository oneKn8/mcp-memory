from __future__ import annotations

from fastmcp import FastMCP

from mcp_memory.config import Config
from mcp_memory.storage import MemoryStore

config = Config.from_env()
store = MemoryStore(config.data_dir)

mcp = FastMCP("mcp-memory")


@mcp.tool()
def remember(
    content: str,
    project: str | None = None,
    tags: list[str] | None = None,
    source: str = "",
    importance: int = 3,
) -> str:
    """Store a memory for later recall. Content is embedded for semantic search.

    Args:
        content: The text content to remember.
        project: Project scope for this memory (default: "global").
        tags: Optional tags for filtering (e.g. ["architecture", "decision"]).
        source: Optional note about where this memory came from.
        importance: Priority 1-5, where 5 is most important (default: 3).
    """
    if not content.strip():
        return "Error: content cannot be empty."

    if importance < 1 or importance > 5:
        return f"Error: importance must be 1-5, got {importance}."

    proj = project or config.default_project
    memory = store.store(
        content=content,
        project=proj,
        tags=tags,
        source=source,
        importance=importance,
    )

    tag_str = f" with tags [{', '.join(memory.tags)}]" if memory.tags else ""
    return (
        f"Stored memory {memory.id} in project '{memory.project}'{tag_str}\n"
        f"Importance: {memory.importance}/5\n"
        f"Timestamp: {memory.timestamp}"
    )


@mcp.tool()
def recall(
    query: str,
    project: str | None = None,
    tags: list[str] | None = None,
    n_results: int | None = None,
    min_relevance: float | None = None,
) -> str:
    """Search memories by semantic similarity.

    Returns the most relevant stored memories.

    Args:
        query: Natural language search query.
        project: Limit search to a specific project (None = search all).
        tags: Filter results to memories with these tags.
        n_results: Maximum results to return (default: 10).
        min_relevance: Minimum relevance score 0.0-1.0 to include.
    """
    if not query.strip():
        return "Error: query cannot be empty."

    n = n_results or config.max_results
    results = store.recall(
        query=query,
        project=project,
        tags=tags,
        n_results=n,
        min_relevance=min_relevance,
    )

    if not results:
        return "No memories found matching your query."

    lines: list[str] = [f"Found {len(results)} matching memories:\n"]
    for i, r in enumerate(results, 1):
        m = r.memory
        tag_str = f"  Tags: {', '.join(m.tags)}\n" if m.tags else ""
        source_str = f"  Source: {m.source}\n" if m.source else ""
        lines.append(
            f"--- [{i}] Relevance: {r.relevance_score:.2f} ---\n"
            f"  ID: {m.id}\n"
            f"  Project: {m.project}\n"
            f"  Content: {m.content}\n"
            f"{tag_str}"
            f"{source_str}"
            f"  Importance: {m.importance}/5\n"
            f"  Stored: {m.timestamp}"
        )

    return "\n".join(lines)


@mcp.tool()
def forget(
    memory_ids: list[str] | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Delete stored memories. Specify at least one filter criterion.

    Args:
        memory_ids: Specific memory IDs to delete.
        project: Delete all memories in this project scope.
        tags: Delete memories matching these tags.
    """
    if not memory_ids and not project and not tags:
        return "Error: specify at least one of memory_ids, project, or tags."

    try:
        count, deleted = store.forget(ids=memory_ids, project=project, tags=tags)
    except ValueError as e:
        return f"Error: {e}"

    if count == 0:
        return "No memories matched the criteria."

    return f"Deleted {count} memories.\nIDs: {', '.join(deleted)}"


@mcp.tool()
def list_memories(
    project: str | None = None,
    tags: list[str] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Browse and list stored memories with optional filtering.

    Args:
        project: Filter to a specific project (None = all projects).
        tags: Filter to memories with these tags.
        page: Page number for pagination (starts at 1).
        page_size: Number of results per page (default: 20).
    """
    if page < 1:
        return "Error: page must be >= 1."
    if page_size < 1:
        return "Error: page_size must be >= 1."

    memories, total, stats = store.list_memories(
        project=project,
        tags=tags,
        page=page,
        page_size=page_size,
    )

    if total == 0:
        return "No memories stored yet."

    start = (page - 1) * page_size + 1
    end = min(start + len(memories) - 1, total)

    lines: list[str] = [f"Showing {start}-{end} of {total} memories (page {page})\n"]

    # Project stats
    if len(stats) > 1 or (len(stats) == 1 and project is None):
        stat_parts = [f"{k}: {v}" for k, v in sorted(stats.items())]
        lines.append(f"Projects: {', '.join(stat_parts)}\n")

    for m in memories:
        tag_str = f"  Tags: {', '.join(m.tags)}\n" if m.tags else ""
        source_str = f"  Source: {m.source}\n" if m.source else ""
        lines.append(
            f"- {m.id}\n"
            f"  Content: {m.content}\n"
            f"  Project: {m.project}\n"
            f"{tag_str}"
            f"{source_str}"
            f"  Importance: {m.importance}/5\n"
            f"  Stored: {m.timestamp}"
        )

    return "\n".join(lines)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
