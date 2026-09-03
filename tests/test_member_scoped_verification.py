"""Tests for Member-Scoped Monorepo Verification & Stop Gate Filtering."""

import os
import tempfile
from typing import List

from framework.core.config import AntiOSConfig, RunnerConfig
from framework.core.gate import resolve_verification_scope, evaluate_stop_gate
from framework.core.topology import WorkspaceTopology, WorkspaceMember


def _create_mock_cargo_workspace(root: str):
    """Creates a mock Cargo workspace with engine and cli crates."""
    cargo_toml = os.path.join(root, "Cargo.toml")
    with open(cargo_toml, "w", encoding="utf-8") as f:
        f.write('[workspace]\nmembers = ["crates/engine", "crates/cli"]\n')

    engine_dir = os.path.join(root, "crates", "engine")
    cli_dir = os.path.join(root, "crates", "cli")
    os.makedirs(engine_dir, exist_ok=True)
    os.makedirs(cli_dir, exist_ok=True)

    with open(os.path.join(engine_dir, "Cargo.toml"), "w", encoding="utf-8") as f:
        f.write('[package]\nname = "engine"\nversion = "0.1.0"\n')

    # cli depends on engine
    with open(os.path.join(cli_dir, "Cargo.toml"), "w", encoding="utf-8") as f:
        f.write('[package]\nname = "cli"\nversion = "0.1.0"\n[dependencies]\nengine = { path = "../engine" }\n')


def test_resolve_scope_standalone_repo():
    """Standalone repo executes all runners."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runners = [
            RunnerConfig(name="pytest", manifest="pyproject.toml", default_command=["pytest"]),
        ]
        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["src/main.py"],
        )
        assert len(scoped) == 1
        assert "Standalone" in reason


def test_resolve_scope_single_member_isolated():
    """Modifying strictly within a leaf member isolates test execution to that member."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_mock_cargo_workspace(tmpdir)

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        # Touching only cli (which has no dependents)
        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["crates/cli/src/main.rs"],
        )
        assert len(scoped) == 1
        assert scoped[0].name == "cli-test"
        assert "isolated to 'cli'" in reason


def test_resolve_scope_dependent_member_blast_radius():
    """Modifying a member whose API is consumed by another member includes both."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_mock_cargo_workspace(tmpdir)

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        # Touching engine (cli depends on engine)
        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["crates/engine/src/lib.rs"],
        )
        # Both engine and dependent cli should be tested
        assert len(scoped) == 2
        runner_names = {r.name for r in scoped}
        assert "engine-test" in runner_names
        assert "cli-test" in runner_names
        assert "plus dependents: cli" in reason


def test_resolve_scope_workflow_override_release():
    """RELEASE and REFACTOR workflows force full workspace verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_mock_cargo_workspace(tmpdir)

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["crates/cli/src/main.rs"],
            workflow="RELEASE",
        )
        assert len(scoped) == 2
        assert "Workflow 'RELEASE' mandates full workspace verification" in reason


def test_resolve_scope_shared_root_escalation():
    """Touching workspace root config escalates to full workspace verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_mock_cargo_workspace(tmpdir)

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["Cargo.toml", "crates/cli/src/main.rs"],
        )
        assert len(scoped) == 2
        assert "Shared workspace root files modified" in reason


def test_resolve_scope_multi_member_escalation():
    """Touching multiple members simultaneously escalates to full workspace validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_mock_cargo_workspace(tmpdir)

        runners = [
            RunnerConfig(name="engine-test", manifest="crates/engine/Cargo.toml", member="engine", default_command=["cargo", "test", "-p", "engine"]),
            RunnerConfig(name="cli-test", manifest="crates/cli/Cargo.toml", member="cli", default_command=["cargo", "test", "-p", "cli"]),
        ]

        scoped, reason = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["crates/engine/src/lib.rs", "crates/cli/src/main.rs"],
        )
        assert len(scoped) == 2
        assert "multiple members" in reason
