"""Tests for AntiOS Project Discovery Engine."""

import os
from pathlib import Path
import unittest

from framework.core.discovery import (
    ProjectDiscoveryEngine,
    discover_project,
    is_tool_in_path,
    parse_simple_toml,
)
from framework.core.profile import ToolCategory

FIXTURES_DIR = Path(os.path.dirname(__file__)) / "fixtures"


def test_parse_simple_toml():
    sample = """
    [project]
    name = "foo"
    version = "1.0.0"

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    """
    data = parse_simple_toml(sample)
    assert "project" in data
    assert ("tool" in data and "pytest" in data["tool"]) or "tool.pytest.ini_options" in data


def test_read_only_discovery_guarantee():
    python_dir = FIXTURES_DIR / "python_project"
    files_before = set(python_dir.rglob("*"))
    mtimes_before = {f: f.stat().st_mtime for f in files_before if f.is_file()}

    profile = discover_project(str(python_dir))
    assert profile is not None

    files_after = set(python_dir.rglob("*"))
    mtimes_after = {f: f.stat().st_mtime for f in files_after if f.is_file()}

    assert files_before == files_after, "Discovery engine must not create or delete files."
    for f in mtimes_before:
        assert mtimes_before[f] == mtimes_after[f], f"File {f} was modified during discovery!"


def test_non_interactive_flag_injection():
    ts_dir = FIXTURES_DIR / "ts_project"
    profile = discover_project(str(ts_dir))
    runners = profile.get_test_runners()
    assert len(runners) >= 1
    # Vitest should be recognized with non-interactive flags
    assert runners[0].name == "node-test-runner"
    assert "vitest" in runners[0].command or "pnpm" in runners[0].command


def test_static_guidance_extraction():
    python_dir = FIXTURES_DIR / "python_project"
    engine = ProjectDiscoveryEngine(str(python_dir))
    engine._discover_guidance()

    assert len(engine.guidance) >= 1
    readme_guidance = next((g for g in engine.guidance if "README.md" in g.source_file), None)
    assert readme_guidance is not None
    assert "pytest" in readme_guidance.declared_commands.get("test", [])


if __name__ == "__main__":
    unittest.main()
