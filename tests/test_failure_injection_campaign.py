"""Boundary Failure-Injection Campaign for AntiOS (12 Stress Scenarios).

Validates that AntiOS fails closed, isolates faults, and prevents state corruption across:
1. Malformed Hook Input (non-dict, empty list, null)
2. Missing Runner Binary in PATH (required runner missing executable)
3. Test Runner Subprocess Execution Failure (exit code != 0)
4. Git Subprocess Command Failure / Unavailable VCS
5. Unsupported / Blocking Unknown Project Archetype (safely deferred)
6. Windows 8.3 Alias Bypass Attempt on Protected Zones
7. Direct Modification Attempt on Upstream Domain Core
8. Corrupt / Malformed antios.config.json
9. Manifest Fingerprint Drift during Adapter Verification
10. Immutable Zone Stripping Attempt (.agents / framework removed from config)
11. Workspace Topology Dependency Graph Cycle / Invalid Syntax
12. Truncated / Corrupt ACTIVE_CONTEXT.md during Session Resumption
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from framework.core.adapter import (
    AdaptationProposal,
    AdaptationProposalItem,
    apply_project_adaptation,
    verify_adapter,
)
from framework.core.changeset import ChangesetPolicy, evaluate_changeset, get_git_changed_files
from framework.core.config import AntiOSConfig, PoliciesConfig, RunnerConfig, load_config
from framework.core.discovery import discover_project
from framework.core.gate import evaluate_stop_gate
from framework.core.guard import evaluate_tool_call
from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskStatus,
    create_task,
    parse_active_context,
    sync_to_active_context,
)
from framework.core.profile import ProjectProfile, UnknownFact
from framework.core.recovery import (
    ContradictionType,
    detect_state_contradictions,
    recover_session,
)
from framework.core.topology import WorkspaceMember, WorkspaceTopology, detect_workspace_topology


def test_failure_01_malformed_hook_input():
    """Failure 1: Stop Gate receives invalid inputs (None, int, string, empty dict, empty workspacePaths)."""
    assert evaluate_stop_gate(None)[0] == "continue"
    assert evaluate_stop_gate("invalid")[0] == "continue"
    assert evaluate_stop_gate(12345)[0] == "continue"
    assert evaluate_stop_gate({})[0] == "continue"
    assert evaluate_stop_gate({"workspacePaths": []})[0] == "continue"
    assert evaluate_stop_gate({"workspacePaths": [""]})[0] == "continue"


def test_failure_02_missing_runner_binary_in_path():
    """Failure 2: Required runner specifies binary not available in system PATH."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(
            test_runners=[
                RunnerConfig(
                    name="nonexistent-runner",
                    default_command=["__definitely_not_on_path_binary_12345__", "test"],
                    required=True,
                )
            ]
        )
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "executable not found in PATH" in reason or "ENVIRONMENT_UNAVAILABLE" in reason or "Required test runtime" in reason


def test_failure_03_test_runner_subprocess_failure():
    """Failure 3: Runner executes but exits with code 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(
            test_runners=[
                RunnerConfig(
                    name="failing-python",
                    default_command=["python", "-c", "import sys; sys.exit(1)"],
                    required=True,
                )
            ]
        )
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "Verification failed" in reason
        assert "Exit Code: 1" in reason


def test_failure_04_git_subprocess_failure():
    """Failure 4: Git status command in uninitialized directory fails closed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Not a git repo -> get_git_changed_files returns []
        files = get_git_changed_files(tmpdir)
        assert files == []

        # If git returns failure on an actual git repo (e.g. broken .git), evaluate_changeset fails closed
        git_dir = Path(tmpdir) / ".git"
        git_dir.mkdir()
        # Invalid git HEAD
        (git_dir / "HEAD").write_text("corrupt content", encoding="utf-8")
        cs_eval = evaluate_changeset(tmpdir, policy=ChangesetPolicy(enabled=True))
        assert cs_eval.is_valid is False
        assert "failed closed" in cs_eval.summary.lower()


def test_failure_05_unsupported_unknown_project_archetype():
    """Failure 5: Project profile with blocking unknown field defers safely without crash."""
    from framework.core.profile import ProjectIdentity
    profile = ProjectProfile(identity=ProjectIdentity(name="test", root_path="/test"))
    profile.unknown_fields.append(
        UnknownFact(
            field_name="unsupported_lang",
            reason="Language COBOL is not supported by AntiOS Core",
            required_action="Requires manual adapter or Core PR",
            is_blocking=True,
        )
    )
    from framework.core.adapter import analyze_adaptation
    proposal = analyze_adaptation(profile)
    deferred = [i for i in proposal.items if i.action.value == "DEFER"]
    assert len(deferred) >= 1
    assert "COBOL" in deferred[0].description or "unsupported_lang" in deferred[0].description


def test_failure_06_windows_8_3_alias_bypass_attempt():
    """Failure 6: Agent attempts to edit framework/ or .agents/ via Windows 8.3 short names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_zones=[".agents", "framework"])
        (Path(tmpdir) / "framework").mkdir()

        alias_payload = {
            "workspacePaths": [tmpdir],
            "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, "FRAME~1", "core", "gate.py")}}
        }
        decision, reason = evaluate_tool_call(alias_payload, config=config)
        assert decision == "deny"
        assert "8.3 alias" in reason or "Self-Protection" in reason or "Boundary Policy" in reason


def test_failure_07_upstream_domain_core_direct_mutation():
    """Failure 7: Agent attempts to directly mutate protected upstream domain component."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_domain_paths=["src/core_engine", "vendor/upstream"])
        payload = {
            "workspacePaths": [tmpdir],
            "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, "src", "core_engine", "state.py")}}
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "deny"
        assert "Boundary Policy" in reason
        assert "core_engine" in reason


def test_failure_08_corrupt_adapter_config_fallback():
    """Failure 8: Corrupt antios.config.json safely falls back to secure default with fail_closed=True."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_config = Path(tmpdir) / "antios.config.json"
        bad_config.write_text("{ unclosed invalid json string...", encoding="utf-8")

        loaded = load_config(tmpdir)
        assert loaded.policies.fail_closed is True
        assert ".agents" in loaded.protected_zones
        assert "framework" in loaded.protected_zones


def test_failure_09_manifest_fingerprint_mismatch_verification():
    """Failure 9: Manifest fingerprint mismatch during adapter verification is flagged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create manifest
        pyproj = Path(tmpdir) / "pyproject.toml"
        pyproj.write_text('[project]\nname = "test"\n', encoding="utf-8")
        (Path(tmpdir) / "tests").mkdir()

        config = AntiOSConfig(
            version="1.0",
            name="Test-Adapter",
            manifest_fingerprint="old_stale_fingerprint_000000000000",
            test_runners=[RunnerConfig(name="unittest", default_command=["python", "-m", "unittest"])]
        )

        res = verify_adapter(tmpdir, config=config, check_fingerprint=True)
        assert res.is_valid is False
        assert any("MANIFEST DRIFT" in issue for issue in res.issues)


def test_failure_10_immutable_zone_stripping_attempt():
    """Failure 10: Proposal attempting to remove .agents or framework fails verification."""
    config = AntiOSConfig(
        version="1.0",
        name="Stripped-Adapter",
        protected_zones=["only_custom_zone"],  # Missing .agents and framework
        test_runners=[RunnerConfig(name="unittest", default_command=["python", "-m", "unittest"])]
    )
    res = verify_adapter(".", config=config, check_fingerprint=False)
    assert res.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION" in issue for issue in res.issues)


def test_failure_11_workspace_topology_graceful_on_malformed_syntax():
    """Failure 11: Directory with invalid package.json / Cargo.toml topology handles syntax errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Invalid JSON in root package.json
        (Path(tmpdir) / "package.json").write_text("{ invalid json", encoding="utf-8")
        topology, members = detect_workspace_topology(tmpdir)
        assert topology == WorkspaceTopology.STANDALONE
        assert members == []


def test_failure_12_corrupt_active_context_resumption():
    """Failure 12: Completely broken ACTIVE_CONTEXT.md recovers gracefully without crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "docs").mkdir()
        ac_file = Path(tmpdir) / "docs" / "ACTIVE_CONTEXT.md"
        ac_file.write_text("random binary \x00\x01 garbage text without any headers", encoding="utf-8")

        plan, state = recover_session(tmpdir, apply_fix=True)
        assert plan is not None
        assert state is not None
        assert state.status == TaskStatus.ACTIVE
