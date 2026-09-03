"""Performance and Latency Benchmarks for AntiOS Core Subsystems.

Validates that AntiOS operates with sub-second responsiveness and strictly bounds overhead:
- Standalone project full verification cycle <= 1.5s
- Medium monorepo (2-5 members) discovery, topology, and scoping <= 2.0s
- Large workspace (10+ members) topological sorting and blast-radius evaluation <= 3.0s
- Task state machine transition and active context serialization <= 50ms
- Security guard evaluation <= 15ms per tool call
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
import unittest

from framework.core.adapter import analyze_adaptation, apply_project_adaptation, verify_adapter
from framework.core.config import AntiOSConfig, RunnerConfig
from framework.core.discovery import discover_project
from framework.core.gate import evaluate_stop_gate, resolve_verification_scope
from framework.core.guard import evaluate_tool_call
from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    create_task,
    sync_to_active_context,
    transition_stage,
)
from framework.core.topology import detect_workspace_topology


def test_perf_standalone_discovery_and_adaptation():
    """Benchmark: Standalone discovery, adaptation proposal, and config verification completes < 1.5s."""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "pyproject.toml").write_text(
            '[project]\nname = "perf-standalone"\nversion = "1.0.0"\n'
            'dependencies = ["requests>=2.28"]\n',
            encoding="utf-8"
        )
        (Path(tmpdir) / "tests").mkdir()

        start = time.perf_counter()
        profile = discover_project(tmpdir)
        proposal = analyze_adaptation(profile)
        apply_project_adaptation(tmpdir, proposal)
        cfg = AntiOSConfig(test_runners=[RunnerConfig(name="test", default_command=["python", "-m", "unittest"])])
        res = verify_adapter(tmpdir, cfg, check_fingerprint=True)
        elapsed = time.perf_counter() - start

        assert res.is_valid is True
        assert elapsed < 1.5, f"Standalone cycle took {elapsed:.3f}s (budget: 1.5s)"


def test_perf_medium_monorepo_topology_and_scoping():
    """Benchmark: 3-member monorepo topology detection and blast-radius calculation < 2.0s."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for m in ["core", "api", "client"]:
            p = Path(tmpdir) / "packages" / m
            p.mkdir(parents=True)
            deps = {"@repo/core": "*"} if m != "core" else {}
            (p / "package.json").write_text(json.dumps({
                "name": f"@repo/{m}",
                "dependencies": deps,
                "scripts": {"test": "echo ok"}
            }))
        (Path(tmpdir) / "package.json").write_text(json.dumps({
            "name": "perf-monorepo",
            "workspaces": ["packages/*"]
        }))

        start = time.perf_counter()
        topology, members = detect_workspace_topology(tmpdir)
        runners = [
            RunnerConfig(name=f"{m}-runner", cwd=f"packages/{m}", default_command=["echo", m])
            for m in ["core", "api", "client"]
        ]
        scoped, _ = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/core/src/index.ts"]
        )
        elapsed = time.perf_counter() - start

        assert len(members) == 3
        assert len(scoped) == 3  # blast radius includes all 3
        assert elapsed < 2.0, f"Medium monorepo cycle took {elapsed:.3f}s (budget: 2.0s)"


def test_perf_large_workspace_blast_radius():
    """Benchmark: 12-member workspace graph resolution and blast radius filtering < 3.0s."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(12):
            name = f"pkg-{i:02d}"
            p = Path(tmpdir) / "packages" / name
            p.mkdir(parents=True)
            # Chain dependencies: pkg-N depends on pkg-(N-1)
            deps = {f"@repo/pkg-{i-1:02d}": "*"} if i > 0 else {}
            (p / "package.json").write_text(json.dumps({
                "name": f"@repo/{name}",
                "dependencies": deps,
                "scripts": {"test": f"echo {name}"}
            }))
        (Path(tmpdir) / "package.json").write_text(json.dumps({
            "name": "large-monorepo",
            "workspaces": ["packages/*"]
        }))

        start = time.perf_counter()
        topology, members = detect_workspace_topology(tmpdir)
        runners = [
            RunnerConfig(name=f"runner-{i:02d}", cwd=f"packages/pkg-{i:02d}", default_command=["echo", f"pkg-{i:02d}"])
            for i in range(12)
        ]
        # Touch root leaf pkg-00 -> blast radius includes all 12 transitive dependents
        scoped, _ = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/pkg-00/src/lib.ts"]
        )
        elapsed = time.perf_counter() - start

        assert len(members) == 12
        assert len(scoped) == 12
        assert elapsed < 3.0, f"Large workspace cycle took {elapsed:.3f}s (budget: 3.0s)"


def test_perf_lifecycle_transition_and_context_sync():
    """Benchmark: Stage transition and ACTIVE_CONTEXT.md synchronization < 50ms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "docs").mkdir()
        task = create_task("M-PERF", TaskClass.FEATURE, RiskTier.LOW)

        start = time.perf_counter()
        for s in [TaskStage.UNDERSTAND, TaskStage.INVESTIGATE, TaskStage.PLAN, TaskStage.IMPLEMENT]:
            transition_stage(task, s)
            sync_to_active_context(task, tmpdir)
        elapsed = time.perf_counter() - start

        # 4 transitions + 4 syncs
        avg_per_op = elapsed / 4.0
        assert avg_per_op < 0.05, f"Lifecycle op took {avg_per_op*1000:.2f}ms (budget: 50ms)"


def test_perf_guard_evaluation():
    """Benchmark: Security guard evaluation < 15ms per call."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(
            protected_zones=[".agents", "framework"],
            protected_domain_paths=["src/auth", "vendor/upstream"]
        )
        payload = {
            "workspacePaths": [tmpdir],
            "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, "src", "app", "router.py")}}
        }

        # Warm up
        evaluate_tool_call(payload, config=config)

        start = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            decision, _ = evaluate_tool_call(payload, config=config)
            assert decision == "allow"
        total_time = time.perf_counter() - start
        avg_call = total_time / iterations

        assert avg_call < 0.015, f"Guard eval took {avg_call*1000:.2f}ms (budget: 15ms)"
