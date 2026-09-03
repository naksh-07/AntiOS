"""Adversarial False-Done Campaign for AntiOS (11 Attack Vectors).

Validates that zero-trust enforcement blocks every attempted variant of false completion:
1. Verbal Claim Only (empty tests array in verdict)
2. Fabricated Test Output (passing summary with non-zero exit code)
3. Wrong Member Runner Executed (leaf A touched, only leaf B executed)
4. Suppressed/Ignored Test Failures (test failed with exit code 1, status falsely set to PASS)
5. Untracked Working Tree Additions (uncommitted/untracked code files)
6. Git Merge Conflict Markers in working tree
7. Outdated Verdict Hash (manifest modified after verdict issuance)
8. Uncommitted Substantive Changes after verifier pass
9. Missing Docs on Code Change under Same Change Set policy
10. Unparseable/Heuristic Verdict Output on HIGH risk task
11. State Machine Stage Jumping (skipping straight to COMPLETE)
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
import unittest

from framework.core.changeset import ChangesetPolicy, evaluate_changeset
from framework.core.config import AntiOSConfig, PoliciesConfig, RunnerConfig
from framework.core.gate import evaluate_stop_gate, resolve_verification_scope
from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskState,
    TaskStatus,
    create_task,
    sync_to_active_context,
    transition_stage,
)
from framework.core.recovery import (
    ContradictionType,
    detect_state_contradictions,
    is_verification_stale,
)
from framework.core.verdict import (
    ResultItem,
    VerificationVerdict,
    evaluate_checker_verdict,
    parse_verdict,
)
from framework.core.worktree import capture_worktree_snapshot


def _init_git_repo(path: str) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "AntiOSTester"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "tester@antios.local"], cwd=path, capture_output=True)


def test_false_done_01_verbal_claim_only():
    """Attack 1: Agent verbally claims tests passed, emitting verdict with empty tests list."""
    verdict = parse_verdict(json.dumps({
        "status": "PASS",
        "risk_tier": "HIGH",
        "files_audited": ["src/payment.py"],
        "tests": [],  # Zero physical tests
        "same_change_set_verified": True,
        "summary": "I reviewed the code thoroughly and it definitely works.",
        "issues": []
    }))
    ok, reason = evaluate_checker_verdict(verdict, required_risk_tier="HIGH")
    assert ok is False
    assert "requires at least one executed physical test result" in reason


def test_false_done_02_fabricated_test_output():
    """Attack 2: Agent claims test passed in summary, but exit_code is non-zero."""
    verdict = parse_verdict(json.dumps({
        "status": "PASS",
        "risk_tier": "HIGH",
        "files_audited": ["src/payment.py"],
        "tests": [{"command": "pytest", "exit_code": 1, "passed": False, "details": "AssertionError: 500 != 200"}],
        "same_change_set_verified": True,
        "summary": "Payment tests all passed cleanly.",
        "issues": []
    }))
    ok, reason = evaluate_checker_verdict(verdict, required_risk_tier="HIGH")
    assert ok is False
    assert "failing test" in reason


def test_false_done_03_wrong_member_runner():
    """Attack 3: Modified code in member A, but only runner for member B was scoped/executed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "package.json").write_text(json.dumps({"name": "root", "workspaces": ["packages/*"]}))
        (Path(tmpdir) / "packages" / "auth").mkdir(parents=True)
        (Path(tmpdir) / "packages" / "billing").mkdir(parents=True)
        (Path(tmpdir) / "packages" / "auth" / "package.json").write_text(json.dumps({"name": "auth"}))
        (Path(tmpdir) / "packages" / "billing" / "package.json").write_text(json.dumps({"name": "billing"}))

        runners = [
            RunnerConfig(name="auth-runner", cwd="packages/auth", default_command=["echo", "auth"]),
            RunnerConfig(name="billing-runner", cwd="packages/billing", default_command=["echo", "billing"]),
        ]
        # Modifying billing, but trying to claim auth was verified
        scoped_runners, rationale = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/billing/src/invoice.ts"],
        )
        assert len(scoped_runners) == 1
        assert scoped_runners[0].name == "billing-runner"
        assert scoped_runners[0].name != "auth-runner"


def test_false_done_04_suppressed_test_failures():
    """Attack 4: Test command returned failure, agent attempts to mark COMPLETE with failing verdict."""
    task = create_task("M-FALSE-DONE-04", TaskClass.FEATURE, RiskTier.HIGH)
    task.current_stage = TaskStage.CONSOLIDATE
    task.verification_verdict = {"status": "FAIL", "summary": "3 tests failed"}

    ok, msg, _ = transition_stage(task, TaskStage.COMPLETE)
    assert ok is False
    assert "failing verifier verdict" in msg or "High-risk task requires verified verdict" in msg


def test_false_done_05_untracked_working_tree_additions():
    """Attack 5: Code changes made in untracked files without tests or verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# App", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)

        # Untracked code file added
        (Path(tmpdir) / "src").mkdir()
        (Path(tmpdir) / "src" / "new_service.py").write_text("class Service: pass", encoding="utf-8")

        config = AntiOSConfig(
            test_runners=[RunnerConfig(name="dummy", default_command=["python", "-c", "exit(0)"])],
            changeset=ChangesetPolicy(enabled=True, require_tests_on_code_change=True)
        )
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "Same Change Set check failed" in reason


def test_false_done_06_git_merge_conflict_markers():
    """Attack 6: Unresolved git merge conflict markers present in repository files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        conflicted_file = Path(tmpdir) / "src" / "conflict.py"
        conflicted_file.parent.mkdir(parents=True)
        conflicted_file.write_text(
            "<<<<<<< HEAD\n"
            "def foo(): return 1\n"
            "=======\n"
            "def foo(): return 2\n"
            ">>>>>>> branch\n",
            encoding="utf-8"
        )

        config = AntiOSConfig(policies=PoliciesConfig(enforce_working_tree_cleanliness=True))
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "Cleanliness check failed" in reason or "conflict" in reason.lower()


def test_false_done_07_outdated_verdict_hash_manifest_drift():
    """Attack 7: Manifest file changed after verifier issued PASS verdict."""
    task = create_task("M-FALSE-DONE-07", TaskClass.FEATURE, RiskTier.HIGH)
    task.verification_verdict = {
        "status": "PASS",
        "summary": "Passed with original manifests",
        "manifest_fingerprint": "hash_version_1",
    }
    task.verification_state = "VERIFIED"

    # Reality on disk has different manifest fingerprint
    stale, reasons = is_verification_stale(
        task,
        dirty_files=[],
        current_manifest_fingerprint="hash_version_2"
    )
    assert stale is True
    assert any("manifest" in r.lower() for r in reasons)


def test_false_done_08_uncommitted_changes_after_verifier_pass():
    """Attack 8: Source files modified after checker approved implementation."""
    task = create_task("M-FALSE-DONE-08", TaskClass.FEATURE, RiskTier.HIGH)
    task.verification_verdict = {
        "status": "PASS",
        "summary": "Approved",
    }
    task.verification_state = "VERIFIED"

    stale, reasons = is_verification_stale(
        task,
        dirty_files=["src/secret.py"],
        current_manifest_fingerprint=""
    )
    assert stale is True
    assert any("working tree files modified" in r.lower() for r in reasons)


def test_false_done_09_missing_docs_on_code_change():
    """Attack 9: Code modified without required docs update under Same Change Set policy."""
    policy = ChangesetPolicy(
        enabled=True,
        require_tests_on_code_change=False,
        require_docs_on_code_change=True,
    )
    eval_res = evaluate_changeset(
        repo_root=".",
        changed_files=["src/core_algo.py"],
        policy=policy,
    )
    assert eval_res.is_valid is False
    assert any("documentation" in v.lower() for v in eval_res.violations)


def test_false_done_10_unparseable_heuristic_verdict():
    """Attack 10: Checker output is unparseable prose containing 'VERDICT: PASS' without JSON."""
    unparseable_text = "I checked everything and the verdict: PASS. Looks solid!"
    v = parse_verdict(unparseable_text)
    # Parser notes parse error in issues
    assert any("Failed to parse formal JSON verdict" in i for i in v.issues)

    # evaluate_checker_verdict strictly rejects heuristic fallback for HIGH/MEDIUM risk
    approved, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert approved is False
    assert "malformed" in reason.lower() or "heuristic" in reason.lower()


def test_false_done_11_state_machine_illegal_skips():
    """Attack 11: Attempting to bypass workflow stages by jumping straight from INTAKE to COMPLETE."""
    task = create_task("M-FALSE-DONE-11", TaskClass.FEATURE, RiskTier.HIGH)
    assert task.current_stage == TaskStage.INTAKE

    # Illegal forward skip directly to COMPLETE
    ok, msg, task = transition_stage(task, TaskStage.COMPLETE)
    assert ok is False
    assert "Invalid stage transition" in msg
    assert task.current_stage == TaskStage.INTAKE
