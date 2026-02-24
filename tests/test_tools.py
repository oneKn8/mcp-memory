from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import mcp_memory.server as server_module
from mcp_memory.config import Config
from mcp_memory.storage import MemoryStore


@pytest.fixture(autouse=True)
def _patch_server(tmp_path: Path) -> None:
    """Patch the server module's global store and config for testing."""
    data_dir = tmp_path / "test-data"
    data_dir.mkdir()
    test_config = Config(data_dir=data_dir, default_project="global", max_results=10)
    test_store = MemoryStore(data_dir)

    with (
        patch.object(server_module, "config", test_config),
        patch.object(server_module, "store", test_store),
    ):
        yield


class TestRememberTool:
    def test_remember_basic(self) -> None:
        result = server_module.remember("test memory content")
        assert "Stored memory" in result
        assert "project 'global'" in result

    def test_remember_with_project(self) -> None:
        result = server_module.remember("test", project="myproject")
        assert "project 'myproject'" in result

    def test_remember_with_tags(self) -> None:
        result = server_module.remember("test", tags=["a", "b"])
        assert "tags [a, b]" in result

    def test_remember_empty_content(self) -> None:
        result = server_module.remember("   ")
        assert "Error" in result

    def test_remember_invalid_importance(self) -> None:
        result = server_module.remember("test", importance=0)
        assert "Error" in result
        result = server_module.remember("test", importance=6)
        assert "Error" in result


class TestRecallTool:
    def test_recall_found(self) -> None:
        server_module.remember("Python is a great programming language")
        result = server_module.recall("programming language")
        assert "Found" in result
        assert "Python" in result

    def test_recall_not_found(self) -> None:
        result = server_module.recall("something that does not exist")
        assert "No memories found" in result

    def test_recall_empty_query(self) -> None:
        result = server_module.recall("   ")
        assert "Error" in result


class TestForgetTool:
    def test_forget_no_criteria(self) -> None:
        result = server_module.forget()
        assert "Error" in result

    def test_forget_by_project(self) -> None:
        server_module.remember("to delete", project="temp")
        result = server_module.forget(project="temp")
        assert "Deleted" in result

    def test_forget_nonexistent(self) -> None:
        result = server_module.forget(memory_ids=["fake-id"])
        assert "No memories matched" in result


class TestListMemoriesTool:
    def test_list_empty(self) -> None:
        result = server_module.list_memories()
        assert "No memories stored" in result

    def test_list_with_memories(self) -> None:
        server_module.remember("first memory")
        server_module.remember("second memory")
        result = server_module.list_memories()
        assert "Showing 1-2 of 2" in result

    def test_list_invalid_page(self) -> None:
        result = server_module.list_memories(page=0)
        assert "Error" in result


class TestFullFlow:
    def test_remember_recall_forget(self) -> None:
        # Store
        remember_result = server_module.remember(
            "Architecture decision: use microservices",
            project="backend",
            tags=["architecture"],
            importance=5,
        )
        assert "Stored memory" in remember_result

        # Recall
        recall_result = server_module.recall(
            "architecture decisions", project="backend"
        )
        assert "microservices" in recall_result

        # List
        list_result = server_module.list_memories(project="backend")
        assert "Showing 1-1 of 1" in list_result

        # Forget
        forget_result = server_module.forget(project="backend")
        assert "Deleted 1" in forget_result

        # Verify deleted
        recall_after = server_module.recall("architecture", project="backend")
        assert "No memories found" in recall_after
