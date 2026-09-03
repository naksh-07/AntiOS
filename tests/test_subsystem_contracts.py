"""Tests for AntiOS Subsystem Contracts.

Validates that all subsystem contracts, data handoffs, and boundary invariants
operate consistently and fail closed across:
1. Discovery -> Profile -> Adapter -> Verification
2. Topology -> Verification Scope -> Stop Gate
3. Changeset -> Stop Gate
4. Maker-Checker -> Verdict Evaluation
5. Active Context -> State Machine -> Recovery
6. Dead-End Memory -> Distillation -> Durable Guidance
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
import unittest

from framework.core.adapter import (
    ActionType,
    AdaptationProposal,
    AdaptationProposalItem,
    ChangeTarget,
    ProposalRisk,
    analyze_adaptation,
    apply_project_adaptation,
    verify_adapter,
)
from framework.core.changeset import (
    ChangesetPolicy,
    evaluate_changeset,
    get_git_changed_files,
)
from framework.core.config import AntiOSConfig, RunnerConfig, load_config
from framework.core.discovery import discover_project
from framework.core.gate import (
    evaluate_stop_gate,
    resolve_verification_scope,
)
from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskState,
    TaskStatus,
    create_task,
    parse_active_context,
    sync_to_active_context,
    transition_stage,
)
from framework.core.profile import ProjectProfile
from framework.core.recovery import (
    ContradictionType,
    detect_state_contradictions,
    is_verification_stale,
    recover_session,
)
from framework.core.topology import WorkspaceMember, WorkspaceTopology, detect_workspace_topology
from framework.core.verdict import (
    ResultItem,
    VerificationVerdict,
    evaluate_checker_verdict,
    parse_verdict,
    prepare_checker_context,
)


def test_contract_discovery_to_adapter_flow():
    """Contract: Discovery produces a ProjectProfile that adapts into a valid AntiOSConfig."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal python project with tests directory
        pyproj = Path(tmpdir) / "pyproject.toml"
        pyproj.write_text(
            '[project]\nname = "contract-demo"\nversion = "0.1.0"\n'
            'dependencies = ["requests>=2.28"]\n',
            encoding="utf-8"
        )
        (Path(tmpdir) / "tests").mkdir()

        profile = discover_project(tmpdir)
        assert profile.manifest_fingerprint != ""
        assert any(t.name == "python-unittest" for t in profile.tools)
        assert profile.identity.name == Path(tmpdir).name

        proposal = analyze_adaptation(profile)
        assert len(proposal.items) > 0

        ok, msg = apply_project_adaptation(tmpdir, proposal)
        assert ok is True

        cfg = load_config(tmpdir)
        assert cfg.manifest_fingerprint == profile.manifest_fingerprint
        assert ".agents" in cfg.protected_zones
        assert "framework" in cfg.protected_zones
        assert cfg.policies.fail_closed is True

        res = verify_adapter(tmpdir, cfg, check_fingerprint=True)
        assert res.is_valid is True, res.issues


def test_contract_topology_to_verification_scope():
    """Contract: Multi-member topology correctly propagates member isolation and blast radius."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup 2 packages: core and cli (cli depends on core)
        core_dir = Path(tmpdir) / "packages" / "core"
        cli_dir = Path(tmpdir) / "packages" / "cli"
        core_dir.mkdir(parents=True)
        cli_dir.mkdir(parents=True)

        (core_dir / "package.json").write_text(json.dumps({"name": "@app/core", "scripts": {"test": "echo test core"}}))
        (cli_dir / "package.json").write_text(json.dumps({
            "name": "@app/cli",
            "dependencies": {"@app/core": "*"},
            "scripts": {"test": "echo test cli"}
        }))
        (Path(tmpdir) / "package.json").write_text(json.dumps({
            "name": "root-monorepo",
            "workspaces": ["packages/*"]
        }))

        runners = [
            RunnerConfig(name="core-runner", manifest="packages/core/package.json", default_command=["echo", "core"], cwd="packages/core"),
            RunnerConfig(name="cli-runner", manifest="packages/cli/package.json", default_command=["echo", "cli"], cwd="packages/cli"),
        ]

        # 1. Modifying leaf cli only -> only cli-runner
        scoped_runners, rationale = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/cli/src/index.ts"]
        )
        assert len(scoped_runners) == 1
        assert scoped_runners[0].name == "cli-runner"

        # 2. Modifying core -> blast radius includes both core and cli
        scoped_runners_blast, rationale_blast = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/core/src/api.ts"]
        )
        assert len(scoped_runners_blast) == 2

        # 3. Touching root package.json -> full workspace escalation
        scoped_runners_root, _ = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["package.json"]
        )
        assert len(scoped_runners_root) == 2


def test_contract_changeset_to_stop_gate():
    """Contract: Same Change Set enforces code/test/doc synchronization inside Stop Gate."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize a real git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)

        # Baseline commit
        f_init = Path(tmpdir) / "README.md"
        f_init.write_text("# Initial", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmpdir, capture_output=True)

        # Uncommitted code change without test
        src_file = Path(tmpdir) / "src" / "app.py"
        src_file.parent.mkdir(parents=True)
        src_file.write_text("def run(): pass\n", encoding="utf-8")

        config = AntiOSConfig(
            test_runners=[RunnerConfig(name="dummy", default_command=["python", "-c", "exit(0)"])],
            changeset=ChangesetPolicy(enabled=True, require_tests_on_code_change=True)
        )

        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "continue"
        assert "Same Change Set check failed" in reason

        # Now add test file
        test_file = Path(tmpdir) / "tests" / "test_app.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_run(): pass\n", encoding="utf-8")

        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "allow"
        assert reason is None


def test_contract_maker_checker_verdict_evaluation():
    """Contract: Maker-Checker context handoff and structured verdict evaluation."""
    context = prepare_checker_context(
        task_id="TASK-M-C",
        objective="Verify implementation of feature",
        risk_tier="HIGH",
        changed_files=["src/logic.py", "tests/test_logic.py"],
        test_commands=["pytest"],
    )
    assert "shallow_depth_law" in context["invariants"]
    assert context["risk_tier"] == "HIGH"

    # Valid passing verdict with physical test records
    verdict_json = json.dumps({
        "status": "PASS",
        "risk_tier": "HIGH",
        "project_member": None,
        "files_audited": ["src/logic.py", "tests/test_logic.py"],
        "tests": [{"command": "pytest", "exit_code": 0, "passed": True, "details": "2 passed"}],
        "same_change_set_verified": True,
        "summary": "Implementation verified cleanly.",
        "issues": []
    })

    v = parse_verdict(verdict_json)
    assert v.status == "PASS"

    approved, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert approved is True
    assert "approved" in reason.lower()

    # Adversarial: Passing status but exit_code 1
    v_failing_test = parse_verdict(json.dumps({
        "status": "PASS",
        "risk_tier": "HIGH",
        "project_member": None,
        "files_audited": ["src/logic.py"],
        "tests": [{"command": "pytest", "exit_code": 1, "passed": False, "details": "AssertionError"}],
        "same_change_set_verified": True,
        "summary": "Claims pass despite test failure",
        "issues": []
    }))
    approved_bad, reason_bad = evaluate_checker_verdict(v_failing_test, required_risk_tier="HIGH")
    assert approved_bad is False
    assert "failing test" in reason_bad.lower()


def test_contract_active_context_to_state_and_recovery():
    """Contract: Active Context serialize/parse roundtrip preserves critical fields and staleness detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task = create_task("M-CONTRACT-RECOVERY", TaskClass.RELEASE_MAINTENANCE, RiskTier.HIGH)
        task.current_stage = TaskStage.VERIFY
        task.status = TaskStatus.VERIFYING
        task.changed_files = ["src/module.py", "docs/API.md"]
        task.verification_verdict = {
            "status": "PASS",
            "summary": "Checker confirmed release readiness",
            "git_head": "abc1234",
            "manifest_fingerprint": "fp9999",
        }

        path = sync_to_active_context(task, tmpdir)
        assert os.path.isfile(path)

        # Ensure active context line count is bounded <= 60 lines
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 60

        recovered_state = parse_active_context(tmpdir)
        assert recovered_state is not None
        assert recovered_state.mission_id == "M-CONTRACT-RECOVERY"
        assert recovered_state.task_class == TaskClass.RELEASE_MAINTENANCE
        assert recovered_state.risk_tier == RiskTier.HIGH
        assert recovered_state.status == TaskStatus.VERIFYING
        assert recovered_state.changed_files == ["src/module.py", "docs/API.md"]
        assert recovered_state.verification_verdict["status"] == "PASS"
        assert recovered_state.verification_verdict["git_head"] == "abc1234"
        assert recovered_state.verification_verdict["manifest_fingerprint"] == "fp9999"

        # Manifest drift invalidation
        stale, reasons = is_verification_stale(
            recovered_state,
            dirty_files=[],
            current_manifest_fingerprint="fp_changed",
            current_git_head="abc1234"
        )
        assert stale is True
        assert any("manifest" in r.lower() for r in reasons)
