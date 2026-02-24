from __future__ import annotations

import pytest

from mcp_memory.storage import MemoryStore


class TestStore:
    def test_store_returns_memory(self, store: MemoryStore) -> None:
        m = store.store("test content", project="global")
        assert m.content == "test content"
        assert m.project == "global"
        assert m.id
        assert m.timestamp

    def test_store_with_tags(self, store: MemoryStore) -> None:
        m = store.store("tagged memory", project="global", tags=["a", "b"])
        assert sorted(m.tags) == ["a", "b"]

    def test_store_with_importance(self, store: MemoryStore) -> None:
        m = store.store("important", project="global", importance=5)
        assert m.importance == 5


class TestRecall:
    def test_semantic_search(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("programming languages", n_results=3)
        assert len(results) > 0
        # Should find Python/Rust related memories
        contents = [r.memory.content for r in results]
        assert any("Python" in c or "Rust" in c for c in contents)

    def test_recall_with_project_filter(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("database", project="infra")
        assert len(results) > 0
        assert all(r.memory.project == "infra" for r in results)

    def test_recall_cross_project(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("database", n_results=10)
        projects = {r.memory.project for r in results}
        # Should find database memories from both infra and ai projects
        assert len(projects) >= 2

    def test_recall_with_tag_filter(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("programming", tags=["python"])
        assert len(results) > 0
        assert all("python" in r.memory.tags for r in results)

    def test_recall_empty_store(self, store: MemoryStore) -> None:
        results = store.recall("anything")
        assert results == []

    def test_recall_relevance_ordering(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("Python scripting", n_results=5)
        if len(results) >= 2:
            scores = [r.relevance_score for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_recall_min_relevance(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall(
            "Python scripting", min_relevance=0.9, n_results=10
        )
        assert all(r.relevance_score >= 0.9 for r in results)

    def test_recall_n_results_limit(self, populated_store: MemoryStore) -> None:
        results = populated_store.recall("anything", n_results=2)
        assert len(results) <= 2


class TestForget:
    def test_forget_by_id(self, store: MemoryStore) -> None:
        m = store.store("to delete", project="global")
        count, deleted = store.forget(ids=[m.id])
        assert count == 1
        assert m.id in deleted
        # Verify it's gone
        results = store.recall("to delete", project="global")
        assert all(r.memory.id != m.id for r in results)

    def test_forget_by_project(self, populated_store: MemoryStore) -> None:
        count, deleted = populated_store.forget(project="dev")
        assert count == 3  # Python, Rust, tests memories

    def test_forget_by_tags(self, populated_store: MemoryStore) -> None:
        count, deleted = populated_store.forget(tags=["database"])
        assert count == 2  # PostgreSQL and ChromaDB

    def test_forget_no_criteria_raises(self, store: MemoryStore) -> None:
        with pytest.raises(ValueError, match="Must specify"):
            store.forget()

    def test_forget_nonexistent(self, store: MemoryStore) -> None:
        count, deleted = store.forget(ids=["nonexistent-id"])
        assert count == 0

    def test_forget_nonexistent_project(self, store: MemoryStore) -> None:
        count, deleted = store.forget(project="nonexistent")
        assert count == 0


class TestListMemories:
    def test_list_all(self, populated_store: MemoryStore) -> None:
        memories, total, stats = populated_store.list_memories()
        assert total == 5
        assert len(memories) == 5

    def test_list_by_project(self, populated_store: MemoryStore) -> None:
        memories, total, stats = populated_store.list_memories(project="dev")
        assert total == 3
        assert all(m.project == "dev" for m in memories)

    def test_list_by_tags(self, populated_store: MemoryStore) -> None:
        memories, total, stats = populated_store.list_memories(tags=["lang"])
        assert total == 2
        assert all("lang" in m.tags for m in memories)

    def test_list_pagination(self, populated_store: MemoryStore) -> None:
        page1, total, _ = populated_store.list_memories(page=1, page_size=2)
        page2, _, _ = populated_store.list_memories(page=2, page_size=2)
        page3, _, _ = populated_store.list_memories(page=3, page_size=2)

        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

        # No overlaps
        all_ids = [m.id for m in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))

    def test_list_project_stats(self, populated_store: MemoryStore) -> None:
        _, _, stats = populated_store.list_memories()
        assert stats["dev"] == 3
        assert stats["infra"] == 1
        assert stats["ai"] == 1

    def test_list_empty(self, store: MemoryStore) -> None:
        memories, total, stats = store.list_memories()
        assert total == 0
        assert memories == []

    def test_list_sorted_by_timestamp(self, store: MemoryStore) -> None:
        store.store("first", project="global")
        store.store("second", project="global")
        store.store("third", project="global")
        memories, _, _ = store.list_memories()
        timestamps = [m.timestamp for m in memories]
        assert timestamps == sorted(timestamps, reverse=True)
