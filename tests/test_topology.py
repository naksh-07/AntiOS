"""Tests for Workspace Topology Detection, Member Representation, and AntiOS Discovery Integration."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.config import AntiOSConfig, RunnerConfig, load_config
from framework.core.discovery import ProjectDiscoveryEngine, discover_project
from framework.core.profile import ProjectIdentity, ProjectProfile, ToolCategory
from framework.core.topology import (
    WorkspaceMember,
    WorkspaceTopology,
    detect_workspace_topology,
    is_safe_relative_path,
    resolve_workspace_patterns,
)


def test_workspace_topology_enum():
    assert WorkspaceTopology.STANDALONE == "STANDALONE"
    assert WorkspaceTopology.PNPM_WORKSPACE == "PNPM_WORKSPACE"
    assert WorkspaceTopology.NPM_WORKSPACE == "NPM_WORKSPACE"
    assert WorkspaceTopology.CARGO_WORKSPACE == "CARGO_WORKSPACE"
    assert WorkspaceTopology.GO_WORKSPACE == "GO_WORKSPACE"
    assert WorkspaceTopology.PYTHON_WORKSPACE == "PYTHON_WORKSPACE"
    assert WorkspaceTopology.POLYGLOT_MONOREPO == "POLYGLOT_MONOREPO"


def test_workspace_member_model():
    member = WorkspaceMember(
        name="@scope/core",
        relative_path="packages/core",
        package_type="typescript",
        manifest_path="packages/core/package.json",
        dependencies=["react", "lodash"],
        is_root=False,
    )
    d = member.to_dict()
    assert d["name"] == "@scope/core"
    assert d["relative_path"] == "packages/core"
    assert d["package_type"] == "typescript"
    assert d["manifest_path"] == "packages/core/package.json"
    assert d["dependencies"] == ["react", "lodash"]
    assert d["is_root"] is False
    assert d["tools"] == []


def test_pnpm_workspace_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create pnpm-workspace.yaml
        (root / "pnpm-workspace.yaml").write_text(
            """packages:
  - 'packages/*'
  - 'apps/*'
  - '!packages/ignored-*'
""",
            encoding="utf-8",
        )
        # Create package directories
        pkg_core = root / "packages" / "core"
        pkg_core.mkdir(parents=True)
        (pkg_core / "package.json").write_text(
            json.dumps({"name": "@repo/core", "dependencies": {"dayjs": "^1.0.0"}, "scripts": {"test": "vitest --run"}}),
            encoding="utf-8",
        )

        pkg_ignored = root / "packages" / "ignored-test"
        pkg_ignored.mkdir(parents=True)
        (pkg_ignored / "package.json").write_text(
            json.dumps({"name": "@repo/ignored"}),
            encoding="utf-8",
        )

        pkg_app = root / "apps" / "web"
        pkg_app.mkdir(parents=True)
        (pkg_app / "package.json").write_text(
            json.dumps({"name": "@repo/web", "devDependencies": {"typescript": "^5.0.0"}, "scripts": {"test:unit": "jest"}}),
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.PNPM_WORKSPACE
        member_names = {m.name for m in members}
        assert "@repo/core" in member_names
        assert "@repo/web" in member_names
        assert "@repo/ignored" not in member_names


def test_npm_workspace_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text(
            json.dumps({
                "name": "npm-monorepo",
                "workspaces": ["modules/*"],
            }),
            encoding="utf-8",
        )
        mod_a = root / "modules" / "mod-a"
        mod_a.mkdir(parents=True)
        (mod_a / "package.json").write_text(
            json.dumps({"name": "mod-a", "scripts": {"test": "mocha", "lint": "eslint ."}}),
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.NPM_WORKSPACE
        assert len(members) == 1
        assert members[0].name == "mod-a"
        assert members[0].package_type == "typescript"
        assert members[0].relative_path == "modules/mod-a"


def test_cargo_workspace_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Cargo.toml").write_text(
            """[workspace]
members = [
    "crates/engine",
    "crates/cli",
]
""",
            encoding="utf-8",
        )
        crate_engine = root / "crates" / "engine"
        crate_engine.mkdir(parents=True)
        (crate_engine / "Cargo.toml").write_text(
            """[package]
name = "engine"
version = "0.1.0"

[dependencies]
serde = "1.0"
""",
            encoding="utf-8",
        )

        crate_cli = root / "crates" / "cli"
        crate_cli.mkdir(parents=True)
        (crate_cli / "Cargo.toml").write_text(
            """[package]
name = "cli"
version = "0.1.0"
""",
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.CARGO_WORKSPACE
        assert len(members) == 2
        names = {m.name for m in members}
        assert "engine" in names
        assert "cli" in names
        engine_member = next(m for m in members if m.name == "engine")
        assert "serde" in engine_member.dependencies


def test_go_workspace_detection_via_gowork():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "go.work").write_text(
            """go 1.22

use (
    ./services/api
    ./services/worker
)
""",
            encoding="utf-8",
        )
        svc_api = root / "services" / "api"
        svc_api.mkdir(parents=True)
        (svc_api / "go.mod").write_text(
            """module example.com/services/api

go 1.22
""",
            encoding="utf-8",
        )

        svc_worker = root / "services" / "worker"
        svc_worker.mkdir(parents=True)
        (svc_worker / "go.mod").write_text(
            """module example.com/services/worker

go 1.22
""",
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.GO_WORKSPACE
        assert len(members) == 2
        names = {m.name for m in members}
        assert "example.com/services/api" in names
        assert "example.com/services/worker" in names


def test_python_workspace_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text(
            """[tool.uv.workspace]
members = ["packages/*"]
""",
            encoding="utf-8",
        )
        pkg_core = root / "packages" / "core"
        pkg_core.mkdir(parents=True)
        (pkg_core / "pyproject.toml").write_text(
            """[project]
name = "my-core"
version = "0.1.0"
dependencies = ["pydantic>=2.0"]
""",
            encoding="utf-8",
        )

        pkg_utils = root / "packages" / "utils"
        pkg_utils.mkdir(parents=True)
        (pkg_utils / "pyproject.toml").write_text(
            """[project]
name = "my-utils"
version = "0.1.0"
""",
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.PYTHON_WORKSPACE
        assert len(members) == 2
        names = {m.name for m in members}
        assert "my-core" in names
        assert "my-utils" in names
        core_member = next(m for m in members if m.name == "my-core")
        assert "pydantic" in core_member.dependencies


def test_polyglot_monorepo_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Rust workspace
        (root / "Cargo.toml").write_text(
            """[workspace]
members = ["rust_crate"]
""",
            encoding="utf-8",
        )
        rc = root / "rust_crate"
        rc.mkdir(parents=True)
        (rc / "Cargo.toml").write_text(
            """[package]
name = "rust_crate"
version = "0.1.0"
""",
            encoding="utf-8",
        )

        # TypeScript pnpm workspace
        (root / "pnpm-workspace.yaml").write_text(
            """packages:
  - 'ts_app'
""",
            encoding="utf-8",
        )
        ta = root / "ts_app"
        ta.mkdir(parents=True)
        (ta / "package.json").write_text(
            json.dumps({"name": "ts-app"}),
            encoding="utf-8",
        )

        topology, members = detect_workspace_topology(str(root))
        assert topology == WorkspaceTopology.POLYGLOT_MONOREPO
        assert len(members) == 2
        types = {m.package_type for m in members}
        assert "rust" in types
        assert "typescript" in types


def test_safe_traversal_ignores_dangerous_directories():
    assert is_safe_relative_path("packages/core") is True
    assert is_safe_relative_path("node_modules/pkg") is False
    assert is_safe_relative_path("target/debug") is False
    assert is_safe_relative_path("vendor/bundle") is False
    assert is_safe_relative_path(".git/refs") is False
    assert is_safe_relative_path(".agents/skills") is False
    assert is_safe_relative_path("dist/bundle.js") is False
    assert is_safe_relative_path("build/output") is False
    assert is_safe_relative_path(".venv/lib") is False


def test_discover_project_workspace_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create pnpm workspace
        (root / "pnpm-workspace.yaml").write_text(
            """packages:
  - 'packages/*'
""",
            encoding="utf-8",
        )
        # Member 1
        pkg_a = root / "packages" / "pkg-a"
        pkg_a.mkdir(parents=True)
        (pkg_a / "package.json").write_text(
            json.dumps({
                "name": "pkg-a",
                "scripts": {
                    "test": "vitest --run",
                    "lint": "eslint .",
                },
            }),
            encoding="utf-8",
        )
        # Member 2
        pkg_b = root / "packages" / "pkg-b"
        pkg_b.mkdir(parents=True)
        (pkg_b / "package.json").write_text(
            json.dumps({
                "name": "pkg-b",
                "scripts": {
                    "test:ci": "jest --watchAll=false",
                },
            }),
            encoding="utf-8",
        )

        profile = discover_project(str(root))
        assert profile.topology == WorkspaceTopology.PNPM_WORKSPACE
        assert len(profile.workspace_members) == 2
        assert profile.manifest_fingerprint != ""
        assert len(profile.manifest_fingerprint) == 64  # SHA-256 hex string

        # Check member-specific tools attached with cwd
        tools = profile.tools
        pkg_a_tools = [t for t in tools if t.cwd == "packages/pkg-a"]
        assert len(pkg_a_tools) >= 1
        test_runner = next(t for t in pkg_a_tools if t.category == ToolCategory.TEST_RUNNER)
        assert test_runner.cwd == "packages/pkg-a"
        assert test_runner.name == "pkg-a-test-runner"

        # Check serialization in profile.to_dict()
        data = profile.to_dict()
        assert data["topology"] == "PNPM_WORKSPACE"
        assert len(data["workspace_members"]) == 2
        assert data["manifest_fingerprint"] == profile.manifest_fingerprint


def test_runner_config_scope_and_member():
    runner = RunnerConfig(
        name="test_member_runner",
        manifest="packages/core/package.json",
        default_command=["pnpm", "test"],
        cwd="packages/core",
        scope="member",
        member="@repo/core",
    )
    assert runner.scope == "member"
    assert runner.member == "@repo/core"
    assert runner.cwd == "packages/core"


def test_load_config_with_scope_and_manifest_fingerprint():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "antios.config.json")
        data = {
            "version": "1.0",
            "name": "WorkspaceConfigTest",
            "manifest_fingerprint": "abc123sha256hash",
            "test_runners": [
                {
                    "name": "core_runner",
                    "manifest": "packages/core/package.json",
                    "default_command": ["pnpm", "test"],
                    "scope": "member",
                    "member": "core",
                    "cwd": "packages/core",
                }
            ],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        cfg = load_config(tmpdir)
        assert cfg.manifest_fingerprint == "abc123sha256hash"
        assert len(cfg.test_runners) == 1
        assert cfg.test_runners[0].scope == "member"
        assert cfg.test_runners[0].member == "core"
        assert cfg.test_runners[0].cwd == "packages/core"
