"""End-to-end Multi-Project Archetype Validation Tests."""

import os
from pathlib import Path
import unittest

from framework.core.discovery import discover_project
from framework.core.profile import ToolCategory

FIXTURES_DIR = Path(os.path.dirname(__file__)) / "fixtures"


def test_python_archetype_validation():
    target = FIXTURES_DIR / "python_project"
    profile = discover_project(str(target))

    assert "Python" in profile.identity.languages
    assert "uv" in profile.identity.package_managers
    assert "FastAPI" in profile.identity.frameworks

    runners = profile.get_test_runners()
    assert any(r.name == "pytest" for r in runners)
    linters = profile.get_linters()
    assert any(l.name == "ruff-check" for l in linters)
    typecheckers = [t for t in profile.tools if t.category == ToolCategory.TYPECHECKER]
    assert any(t.name == "mypy-typecheck" for t in typecheckers)


def test_typescript_archetype_validation():
    target = FIXTURES_DIR / "ts_project"
    profile = discover_project(str(target))

    assert "TypeScript / JavaScript" in profile.identity.languages
    assert "pnpm" in profile.identity.package_managers
    assert "React" in profile.identity.frameworks

    runners = profile.get_test_runners()
    assert any(r.name == "node-test-runner" for r in runners)
    typecheckers = [t for t in profile.tools if t.category == ToolCategory.TYPECHECKER]
    assert any(t.name == "typescript-check" for t in typecheckers)


def test_go_archetype_validation():
    target = FIXTURES_DIR / "go_project"
    profile = discover_project(str(target))

    assert "Go" in profile.identity.languages
    assert "go" in profile.identity.build_systems

    runners = profile.get_test_runners()
    assert any(r.name == "go-test-runner" for r in runners)
    linters = profile.get_linters()
    assert any(l.name == "golangci-lint" for l in linters)


def test_rust_archetype_validation():
    target = FIXTURES_DIR / "rust_project"
    profile = discover_project(str(target))

    assert "Rust" in profile.identity.languages
    assert "cargo" in profile.identity.build_systems

    runners = profile.get_test_runners()
    assert any(r.name == "cargo-test-runner" for r in runners)
    linters = profile.get_linters()
    assert any(l.name == "cargo-clippy" for l in linters)
    formatters = [t for t in profile.tools if t.category == ToolCategory.FORMATTER]
    assert any(f.name == "rustfmt-check" for f in formatters)


def test_unknown_partial_environment_validation():
    target = FIXTURES_DIR / "unknown_project"
    profile = discover_project(str(target))

    # Must NOT hallucinate languages or runners
    assert len(profile.identity.languages) == 0
    assert len(profile.get_test_runners()) == 0

    # Must record explicit UNKNOWN facts
    unknown_fields = [u.field_name for u in profile.unknown_fields]
    assert "project_language" in unknown_fields
    assert "git_repository" in unknown_fields

    blocking_unknowns = [u for u in profile.unknown_fields if u.is_blocking]
    assert len(blocking_unknowns) >= 1
    assert blocking_unknowns[0].field_name == "project_language"


def test_ts_monorepo_archetype_validation():
    target = FIXTURES_DIR / "ts_monorepo"
    profile = discover_project(str(target))

    assert profile.topology.value == "PNPM_WORKSPACE"
    assert len(profile.workspace_members) == 2
    member_names = [m.name for m in profile.workspace_members]
    assert "@monorepo/core" in member_names
    assert "@monorepo/ui" in member_names

    # Check member tools have scoped cwd
    core_member = next(m for m in profile.workspace_members if m.name == "@monorepo/core")
    assert any(t.category == ToolCategory.TEST_RUNNER for t in core_member.tools)
    assert any(t.cwd and t.cwd.replace("\\", "/") == "packages/core" for t in core_member.tools)


def test_cargo_workspace_archetype_validation():
    target = FIXTURES_DIR / "cargo_workspace"
    profile = discover_project(str(target))

    assert profile.topology.value == "CARGO_WORKSPACE"
    assert len(profile.workspace_members) == 2
    member_names = [m.name for m in profile.workspace_members]
    assert "engine" in member_names
    assert "cli" in member_names


def test_go_workspace_archetype_validation():
    target = FIXTURES_DIR / "go_workspace"
    profile = discover_project(str(target))

    assert profile.topology.value == "GO_WORKSPACE"
    assert len(profile.workspace_members) == 2
    member_names = [m.name for m in profile.workspace_members]
    assert "example.com/services/auth" in member_names
    assert "example.com/services/api" in member_names


if __name__ == "__main__":
    unittest.main()

