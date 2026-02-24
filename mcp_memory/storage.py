from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import chromadb

from mcp_memory.models import Memory, RecallResult

TAG_PREFIX = "tag_"


def _collection_name(project: str) -> str:
    safe = project.replace("-", "_").replace(" ", "_").lower()
    return f"memories_{safe}"


def _tags_to_metadata(tags: list[str]) -> dict[str, object]:
    meta: dict[str, object] = {"tags": ",".join(sorted(tags))}
    for tag in tags:
        meta[f"{TAG_PREFIX}{tag}"] = True
    return meta


def _metadata_to_tags(metadata: dict[str, object]) -> list[str]:
    tags_str = str(metadata.get("tags", ""))
    if not tags_str:
        return []
    return tags_str.split(",")


def _memory_from_chroma(
    id: str,
    document: str,
    metadata: dict[str, object],
) -> Memory:
    return Memory(
        id=id,
        content=document,
        project=str(metadata.get("project", "global")),
        tags=_metadata_to_tags(metadata),
        source=str(metadata.get("source", "")),
        importance=int(metadata.get("importance", 3)),
        timestamp=str(metadata.get("timestamp", "")),
    )


class MemoryStore:
    def __init__(self, data_dir: Path) -> None:
        self._client = chromadb.PersistentClient(path=str(data_dir))

    def _get_collection(self, project: str) -> chromadb.Collection:
        return self._client.get_or_create_collection(
            name=_collection_name(project),
            metadata={"hnsw:space": "cosine"},
        )

    def _list_project_names(self) -> list[str]:
        collections = self._client.list_collections()
        prefix = "memories_"
        return [c.name[len(prefix) :] for c in collections if c.name.startswith(prefix)]

    def store(
        self,
        content: str,
        project: str,
        tags: list[str] | None = None,
        source: str = "",
        importance: int = 3,
    ) -> Memory:
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        tags = tags or []

        metadata: dict[str, object] = {
            "project": project,
            "source": source,
            "importance": importance,
            "timestamp": timestamp,
        }
        metadata.update(_tags_to_metadata(tags))

        collection = self._get_collection(project)
        collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[metadata],
        )

        return Memory(
            id=memory_id,
            content=content,
            project=project,
            tags=tags,
            source=source,
            importance=importance,
            timestamp=timestamp,
        )

    def recall(
        self,
        query: str,
        project: str | None = None,
        tags: list[str] | None = None,
        n_results: int = 10,
        min_relevance: float | None = None,
    ) -> list[RecallResult]:
        projects = [project] if project else self._list_project_names()
        if not projects:
            return []

        all_results: list[RecallResult] = []

        for proj in projects:
            collection = self._get_collection(proj)
            if collection.count() == 0:
                continue

            where = self._build_tag_filter(tags)
            actual_n = min(n_results, collection.count())
            if actual_n < 1:
                continue

            result = collection.query(
                query_texts=[query],
                n_results=actual_n,
                where=where,
            )

            ids = result["ids"][0] if result["ids"] else []
            documents = result["documents"][0] if result["documents"] else []
            metadatas = result["metadatas"][0] if result["metadatas"] else []
            distances = result["distances"][0] if result["distances"] else []

            for i, mid in enumerate(ids):
                distance = distances[i]
                # Cosine distance: 0 = identical, 2 = opposite
                # Convert to 0-1 relevance score
                relevance = 1.0 - (distance / 2.0)

                if min_relevance is not None and relevance < min_relevance:
                    continue

                memory = _memory_from_chroma(mid, documents[i], metadatas[i])
                all_results.append(
                    RecallResult(
                        memory=memory,
                        relevance_score=relevance,
                        distance=distance,
                    )
                )

        all_results.sort(key=lambda r: r.relevance_score, reverse=True)
        return all_results[:n_results]

    def forget(
        self,
        ids: list[str] | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
    ) -> tuple[int, list[str]]:
        if not ids and not project and not tags:
            raise ValueError("Must specify at least one of: ids, project, tags")

        deleted_ids: list[str] = []

        if ids:
            # Delete specific IDs -- search all projects
            for proj in self._list_project_names():
                collection = self._get_collection(proj)
                existing = collection.get(ids=ids)
                found = existing["ids"]
                if found:
                    collection.delete(ids=found)
                    deleted_ids.extend(found)

        elif project and not tags:
            # Delete entire project
            col_name = _collection_name(project)
            try:
                collection = self._client.get_collection(col_name)
                all_items = collection.get()
                deleted_ids.extend(all_items["ids"])
                self._client.delete_collection(col_name)
            except Exception:
                pass

        elif tags:
            # Delete by tags, optionally scoped to project
            projects = [project] if project else self._list_project_names()
            where = self._build_tag_filter(tags)
            if where:
                for proj in projects:
                    collection = self._get_collection(proj)
                    matching = collection.get(where=where)
                    found = matching["ids"]
                    if found:
                        collection.delete(ids=found)
                        deleted_ids.extend(found)

        return len(deleted_ids), deleted_ids

    def list_memories(
        self,
        project: str | None = None,
        tags: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Memory], int, dict[str, int]]:
        projects = [project] if project else self._list_project_names()

        all_memories: list[Memory] = []
        project_stats: dict[str, int] = {}

        where = self._build_tag_filter(tags)

        for proj in projects:
            collection = self._get_collection(proj)
            if where:
                result = collection.get(where=where)
            else:
                result = collection.get()

            ids = result["ids"]
            documents = result["documents"] or []
            metadatas = result["metadatas"] or []

            project_stats[proj] = len(ids)

            for i, mid in enumerate(ids):
                memory = _memory_from_chroma(mid, documents[i], metadatas[i])
                all_memories.append(memory)

        # Sort by timestamp descending (newest first)
        all_memories.sort(key=lambda m: m.timestamp, reverse=True)

        total = len(all_memories)
        start = (page - 1) * page_size
        end = start + page_size
        page_memories = all_memories[start:end]

        return page_memories, total, project_stats

    @staticmethod
    def _build_tag_filter(
        tags: list[str] | None,
    ) -> dict[str, object] | None:
        if not tags:
            return None
        if len(tags) == 1:
            return {f"{TAG_PREFIX}{tags[0]}": True}
        # Multiple tags: match memories containing ALL tags
        return {"$and": [{f"{TAG_PREFIX}{t}": True} for t in tags]}
