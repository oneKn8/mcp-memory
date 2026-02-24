from __future__ import annotations

from pathlib import Path

import pytest

from mcp_memory.storage import MemoryStore


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "mcp-memory-test"
    d.mkdir()
    return d


@pytest.fixture()
def store(data_dir: Path) -> MemoryStore:
    return MemoryStore(data_dir)


@pytest.fixture()
def populated_store(store: MemoryStore) -> MemoryStore:
    store.store("Python is great for scripting", project="dev", tags=["python", "lang"])
    store.store("Rust is fast and safe", project="dev", tags=["rust", "lang"])
    store.store(
        "Use PostgreSQL for relational data", project="infra", tags=["database"]
    )
    store.store(
        "ChromaDB is good for embeddings", project="ai", tags=["database", "ml"]
    )
    store.store("Always write tests before shipping", project="dev", tags=["testing"])
    return store
