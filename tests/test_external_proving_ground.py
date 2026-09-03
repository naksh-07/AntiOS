"""Tests for External Proving Ground Validation & Execution Telemetry."""

import os
import tempfile
import json

from framework.core.discovery import discover_project
from framework.core.adapter import analyze_adaptation, generate_adapter_config, verify_adapter
from framework.core.topology import detect_workspace_topology, WorkspaceTopology
from framework.core.telemetry import (
    ExecutionTelemetryRecord,
    record_telemetry,
    load_telemetry,
    summarize_telemetry,
)

REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
CLICK_PATH = os.path.join(REPO_ROOT, "sandbox", "proving_ground", "click")
STUDYLAB_PATH = os.path.join(REPO_ROOT, "sandbox", "StudyLab")


def test_click_proving_ground_discovery():
    """Verify read-only discovery on real pallets/click external repository."""
    if not os.path.isdir(CLICK_PATH):
        # Skip if sandbox clone is not present
        return

    profile = discover_project(CLICK_PATH)
    assert profile.identity.name == "click"
    assert "Python" in profile.identity.languages
    assert "uv" in profile.identity.package_managers or "pip" in profile.identity.package_managers

    # Verify observed facts
    observed_paths = [f.path for f in profile.observed_facts]
    assert "pyproject.toml" in observed_paths

    # Verify inferred facts
    inferred_hypotheses = [f.hypothesis for f in profile.inferred_facts]
    assert any("pytest" in h.lower() for h in inferred_hypotheses)

    # Verify tools discovered
    tool_names = [t.name for t in profile.tools]
    assert any("pytest" in n for n in tool_names)
    assert any("ruff" in n for n in tool_names)


def test_click_adaptation_proposal_and_adapter_generation():
    """Verify adaptation proposal and adapter configuration for pallets/click."""
    if not os.path.isdir(CLICK_PATH):
        return

    profile = discover_project(CLICK_PATH)
    proposal = analyze_adaptation(profile)

    # Core change denial: zero items should target ANTIOS_CORE
    for item in proposal.items:
        assert item.target.value != "ANTIOS_CORE", "Project adaptation must never mutate ANTIOS_CORE"

    # Adapter config generation
    adapter_cfg = generate_adapter_config(profile, proposal)
    assert adapter_cfg.name == "AntiOS-click-Adapter"
    assert ".agents" in adapter_cfg.protected_zones
    assert "framework" in adapter_cfg.protected_zones
    assert adapter_cfg.policies.fail_closed is True
    assert len(adapter_cfg.test_runners) > 0


def test_click_adapter_verification():
    """Verify adapter verification pipeline enforces invariants on click adapter."""
    if not os.path.isdir(CLICK_PATH):
        return

    profile = discover_project(CLICK_PATH)
    proposal = analyze_adaptation(profile)
    adapter_cfg = generate_adapter_config(profile, proposal)

    result = verify_adapter(CLICK_PATH, adapter_cfg)
    # Protected zones and fail-closed must be verified
    assert any(".agents" in c for c in result.passed_checks)
    assert any("framework" in c for c in result.passed_checks)
    assert any("fail-closed" in c.lower() for c in result.passed_checks)


def test_studylab_polyglot_monorepo_discovery():
    """Verify read-only discovery on StudyLab polyglot monorepo proving ground."""
    if not os.path.isdir(STUDYLAB_PATH):
        return

    topo, members = detect_workspace_topology(STUDYLAB_PATH)
    assert topo == WorkspaceTopology.POLYGLOT_MONOREPO
    assert len(members) > 5

    member_names = {m.name for m in members}
    assert "anki_proto" in member_names or any("anki" in n for n in member_names)


def test_execution_telemetry_recording_and_summary():
    """Verify execution telemetry logging, loading, and aggregation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rec1 = ExecutionTelemetryRecord(
            task_id="TASK-T1",
            task_risk="HIGH",
            checker_dispatched=True,
            verification_duration_ms=450.0,
            failures_detected_by_checker=1,
            final_verdict="PASS",
            scoped_members=["core"],
            tested_files=["src/core.py"],
        )
        rec2 = ExecutionTelemetryRecord(
            task_id="TASK-T2",
            task_risk="LOW",
            checker_dispatched=False,
            verification_duration_ms=120.0,
            failures_detected_by_checker=0,
            final_verdict="PASS",
            scoped_members=[],
            tested_files=["README.md"],
        )

        record_telemetry(tmpdir, rec1)
        record_telemetry(tmpdir, rec2)

        loaded = load_telemetry(tmpdir, "TASK-T1")
        assert loaded is not None
        assert loaded.task_risk == "HIGH"
        assert loaded.failures_detected_by_checker == 1

        summary = summarize_telemetry(tmpdir)
        assert summary["total_tasks"] == 2
        assert summary["checker_dispatched_count"] == 1
        assert summary["pass_rate"] == 1.0
        assert summary["total_failures_caught"] == 1
        assert summary["avg_verification_duration_ms"] == 285.0
