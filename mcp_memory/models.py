from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Memory:
    id: str
    content: str
    project: str
    tags: list[str] = field(default_factory=list)
    source: str = ""
    importance: int = 3
    timestamp: str = ""


@dataclass
class RecallResult:
    memory: Memory
    relevance_score: float
    distance: float
