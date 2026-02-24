from __future__ import annotations

from pathlib import Path

import pytest

from mcp_memory.config import Config


def test_default_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    default_dir = tmp_path / ".mcp-memory"
    monkeypatch.setenv("MCP_MEMORY_DATA_DIR", str(default_dir))
    monkeypatch.delenv("MCP_MEMORY_DEFAULT_PROJECT", raising=False)
    monkeypatch.delenv("MCP_MEMORY_MAX_RESULTS", raising=False)

    cfg = Config.from_env()
    assert cfg.data_dir == default_dir
    assert cfg.default_project == "global"
    assert cfg.max_results == 10
    assert default_dir.exists()


def test_custom_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    custom_dir = tmp_path / "custom"
    monkeypatch.setenv("MCP_MEMORY_DATA_DIR", str(custom_dir))
    monkeypatch.setenv("MCP_MEMORY_DEFAULT_PROJECT", "myproject")
    monkeypatch.setenv("MCP_MEMORY_MAX_RESULTS", "25")

    cfg = Config.from_env()
    assert cfg.data_dir == custom_dir
    assert cfg.default_project == "myproject"
    assert cfg.max_results == 25


def test_invalid_max_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_MEMORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MCP_MEMORY_MAX_RESULTS", "0")

    with pytest.raises(ValueError, match="must be >= 1"):
        Config.from_env()


def test_negative_max_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_MEMORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MCP_MEMORY_MAX_RESULTS", "-5")

    with pytest.raises(ValueError, match="must be >= 1"):
        Config.from_env()
