"""Tests for framework.core.gate."""

import json
import os
import tempfile

from framework.core.config import AntiOSConfig, TestRunnerConfig
from framework.core.gate import discover_test_runners, evaluate_stop_gate


def test_gate_allows_when_no_runner_in_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload)
        assert decision == "allow"
        assert reason is None


def test_gate_detects_and_runs_passing_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create manifest
        pkg = {"name": "test-pkg", "scripts": {"test": "python -c \"exit(0)\""}}
        with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg, f)

        runner = TestRunnerConfig(
            name="mock_node",
            manifest="package.json",
            scripts=["test"],
            default_command=["python", "-c", "exit(0)"]
        )
        config = AntiOSConfig(test_runners=[runner])

        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "allow"


def test_gate_blocks_on_failing_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Manifest pointing to failing command
        with open(os.path.join(tmpdir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write("[project]\nname = 'test'")

        runner = TestRunnerConfig(
            name="mock_pytest",
            manifest="pyproject.toml",
            default_command=["python", "-c", "import sys; sys.stderr.write('AssertionError: expected 1 got 0'); sys.exit(1)"]
        )
        config = AntiOSConfig(test_runners=[runner])

        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "continue"
        assert "Verification failed" in reason
        assert "AssertionError" in reason


def test_gate_fail_closed_on_malformed_input():
    decision, reason = evaluate_stop_gate(None)
    assert decision == "continue"
    assert "Failing closed" in reason


def test_gate_auto_discovers_manifests():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Node package.json with vitest
        with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as f:
            json.dump({"scripts": {"vitest:once": "vitest run"}}, f)
        runners = discover_test_runners(tmpdir)
        assert len(runners) == 1
        assert runners[0].name == "vitest"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Python pyproject.toml
        with open(os.path.join(tmpdir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write("[tool.pytest.ini_options]\n")
        runners = discover_test_runners(tmpdir)
        assert len(runners) == 1
        assert runners[0].name == "pytest"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Rust Cargo.toml
        with open(os.path.join(tmpdir, "Cargo.toml"), "w", encoding="utf-8") as f:
            f.write("[package]\nname = \"test\"\n")
        runners = discover_test_runners(tmpdir)
        assert len(runners) == 1
        assert runners[0].name == "cargo-test"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Go go.mod
        with open(os.path.join(tmpdir, "go.mod"), "w", encoding="utf-8") as f:
            f.write("module example.com/mod\n")
        runners = discover_test_runners(tmpdir)
        assert len(runners) == 1
        assert runners[0].name == "go-test"
