from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    data_dir: Path
    default_project: str
    max_results: int

    @classmethod
    def from_env(cls) -> Config:
        data_dir = Path(
            os.environ.get("MCP_MEMORY_DATA_DIR", "~/.mcp-memory")
        ).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)

        default_project = os.environ.get("MCP_MEMORY_DEFAULT_PROJECT", "global")

        max_results_str = os.environ.get("MCP_MEMORY_MAX_RESULTS", "10")
        max_results = int(max_results_str)
        if max_results < 1:
            raise ValueError(f"MCP_MEMORY_MAX_RESULTS must be >= 1, got {max_results}")

        return cls(
            data_dir=data_dir,
            default_project=default_project,
            max_results=max_results,
        )
