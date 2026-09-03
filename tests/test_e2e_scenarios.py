"""End-to-End Integration Scenarios A through H for AntiOS.

Validates that the complete AntiOS system works coherently end-to-end:
- Scenario A: Clean Feature Run (Intake -> Plan -> Implement -> Test -> Verify -> Complete)
- Scenario B: TDD Flow (Failing test -> Stop Gate blocks -> Implementation -> Stop Gate allows)
- Scenario C: Bug Fix Flow (Bug reproduction -> Fix -> Verification pass)
- Scenario D: Refactor with Invariant Protection (Self-protection guard + same change set)
- Scenario E: Interrupted Session & Context Resumption (Preserves bounded ACTIVE_CONTEXT.md)
- Scenario F: Verification Demotion on Late Code Modification (Stale verification detection)
- Scenario G: Multi-Member Monorepo Scoped vs Full Escalation (Leaf vs Blast Radius vs Root)
- Scenario H: Dead-End Memory & Recurrence Distillation (Candidate -> Recurrence -> Promoted)
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
    analyze_adaptation,
    apply_project_adaptation,
    verify_adapter,
)
from framework.core.changeset import ChangesetPolicy, evaluate_changeset
from framework.core.config import AntiOSConfig, PoliciesConfig, RunnerConfig, load_config
from framework.core.discovery import discover_project
from framework.core.gate import evaluate_stop_gate, resolve_verification_scope
from framework.core.guard import evaluate_tool_call
from framework.core.lifecycle import (
    ORDERED_STAGES,
    RiskTier,
    TaskClass,
    TaskStage,
    TaskState,
    TaskStatus,
    create_task,
    interrupt_task,
    parse_active_context,
    recover_task,
    sync_to_active_context,
    transition_stage,
)
from framework.core.memory import (
    DeterministicLessonMatcher,
    KnowledgeAuthority,
    LessonDistillationEngine,
    LessonRecord,
    format_lessons,
    parse_lessons,
)
from framework.core.recovery import (
    ContradictionType,
    detect_state_contradictions,
    is_verification_stale,
    recover_session,
)
from framework.core.verdict import (
    ResultItem,
    VerificationVerdict,
    evaluate_checker_verdict,
    parse_verdict,
    prepare_checker_context,
)
from framework.core.worktree import capture_worktree_snapshot


def _init_git_repo(path: str) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "AntiOSTester"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "tester@antios.local"], cwd=path, capture_output=True)


def test_scenario_a_clean_feature_run():
    """Scenario A: Clean Feature Run from INTAKE to COMPLETE with Maker-Checker."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        (Path(tmpdir) / "docs").mkdir()

        task = create_task("M-SCENARIO-A", TaskClass.FEATURE, RiskTier.HIGH)
        assert task.current_stage == TaskStage.INTAKE

        # Progress through INTAKE -> UNDERSTAND -> INVESTIGATE -> PLAN
        for stage in [TaskStage.UNDERSTAND, TaskStage.INVESTIGATE, TaskStage.PLAN]:
            ok, _, task = transition_stage(task, stage)
            assert ok is True

        # Implement stage
        ok, _, task = transition_stage(task, TaskStage.IMPLEMENT)
        assert ok is True
        task.changed_files = ["src/billing.py", "tests/test_billing.py", "docs/billing.md"]
        sync_to_active_context(task, tmpdir)

        # Test stage
        ok, _, task = transition_stage(task, TaskStage.TEST, evidence={"test_exit_code": 0})
        assert ok is True

        # Verify stage (Maker-Checker dispatch)
        ok, _, task = transition_stage(task, TaskStage.VERIFY)
        assert ok is True
        assert task.status == TaskStatus.VERIFYING

        # Verifier audits and submits verdict
        verdict_data = {
            "status": "PASS",
            "risk_tier": "HIGH",
            "files_audited": task.changed_files,
            "tests": [{"command": "pytest tests/test_billing.py", "exit_code": 0, "passed": True, "details": "3 passed"}],
            "same_change_set_verified": True,
            "summary": "Audited billing module and verified clean pass",
            "issues": [],
            "git_head": "commit-001",
            "manifest_fingerprint": "fp-1234",
        }
        verdict = parse_verdict(json.dumps(verdict_data))
        approved, _ = evaluate_checker_verdict(verdict, required_risk_tier="HIGH")
        assert approved is True

        task.verification_verdict = verdict_data
        task.verification_state = "VERIFIED"
        sync_to_active_context(task, tmpdir)

        # Review -> Consolidate -> Complete
        ok, _, task = transition_stage(task, TaskStage.REVIEW)
        assert ok is True
        ok, _, task = transition_stage(task, TaskStage.CONSOLIDATE)
        assert ok is True
        ok, _, task = transition_stage(task, TaskStage.COMPLETE)
        assert ok is True
        assert task.status == TaskStatus.COMPLETED


def test_scenario_b_tdd_flow():
    """Scenario B: TDD Flow — Failing test blocks Stop Gate until implementation passes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        (Path(tmpdir) / "tests").mkdir()
        (Path(tmpdir) / "src").mkdir()

        # Commit initial state
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# App", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True)

        # 1. Author failing test
        test_file = Path(tmpdir) / "tests" / "test_feature.py"
        test_file.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")

        config = AntiOSConfig(
            test_runners=[
                RunnerConfig(name="pytest", default_command=["python", "tests/test_feature.py"], required=True)
            ],
            policies=PoliciesConfig(fail_closed=True, enforce_same_change_set=False, enforce_working_tree_cleanliness=False)
        )

        # Stop Gate must block completion
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "Verification failed" in reason

        # 2. Provide working implementation
        test_file.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")

        # Stop Gate allows completion
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "allow"
        assert reason is None


def test_scenario_c_bug_fix_flow():
    """Scenario C: Bug Fix Lifecycle with state machine backward and forward transitions."""
    task = create_task("BUG-404", TaskClass.BUG, RiskTier.MEDIUM)
    for s in [TaskStage.UNDERSTAND, TaskStage.INVESTIGATE, TaskStage.PLAN, TaskStage.IMPLEMENT]:
        transition_stage(task, s)

    # Move to TEST
    transition_stage(task, TaskStage.TEST)

    # Test fails reproduction -> recover back to IMPLEMENT
    ok, msg, task = transition_stage(task, TaskStage.IMPLEMENT, evidence={"repro_failure": "AssertionError: expected 200 got 500"})
    assert ok is True
    assert task.current_stage == TaskStage.IMPLEMENT
    assert "repro_failure" in task.metadata

    # Implement fix -> re-advance to TEST -> VERIFY -> COMPLETE
    transition_stage(task, TaskStage.TEST, evidence={"repro_passed": True})
    transition_stage(task, TaskStage.VERIFY)
    transition_stage(task, TaskStage.REVIEW)
    transition_stage(task, TaskStage.CONSOLIDATE)
    ok, _, task = transition_stage(task, TaskStage.COMPLETE)
    assert ok is True
    assert task.status == TaskStatus.COMPLETED


def test_scenario_d_refactor_invariant_protection():
    """Scenario D: Refactoring enforces self-protection guard and same change set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        (Path(tmpdir) / ".agents").mkdir()
        (Path(tmpdir) / "framework").mkdir()

        config = AntiOSConfig(
            protected_zones=[".agents", "framework"],
            protected_domain_paths=["src/core_auth"]
        )

        # 1. Guard blocks modification to .agents
        decision, reason = evaluate_tool_call(
            {"workspacePaths": [tmpdir], "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, ".agents", "rules.md")}}},
            config=config
        )
        assert decision == "deny"
        assert "Self-Protection" in reason

        # 2. Guard blocks modification to protected upstream domain
        decision, reason = evaluate_tool_call(
            {"workspacePaths": [tmpdir], "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, "src", "core_auth", "keys.py")}}},
            config=config
        )
        assert decision == "deny"
        assert "Boundary Policy" in reason

        # 3. Guard allows application code edit
        decision, reason = evaluate_tool_call(
            {"workspacePaths": [tmpdir], "toolCall": {"args": {"TargetFile": os.path.join(tmpdir, "src", "ui", "button.py")}}},
            config=config
        )
        assert decision == "allow"


def test_scenario_e_interrupted_session_and_resumption():
    """Scenario E: Interrupted session preserves context, recovers cleanly within 60-line budget."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        (Path(tmpdir) / "docs").mkdir()

        task = create_task("M-SESSION-RECOVER", TaskClass.FEATURE, RiskTier.MEDIUM)
        transition_stage(task, TaskStage.UNDERSTAND)
        transition_stage(task, TaskStage.INVESTIGATE)
        transition_stage(task, TaskStage.PLAN)
        transition_stage(task, TaskStage.IMPLEMENT)

        task.changed_files = ["src/service.py"]
        task.blockers = ["Waiting on API credentials"]
        task.next_action = "Obtain test sandbox keys"

        interrupt_task(task, "User paused work")
        assert task.status == TaskStatus.INTERRUPTED

        sync_to_active_context(task, tmpdir)

        # Validate file written and <= 60 lines
        ac_file = Path(tmpdir) / "docs" / "ACTIVE_CONTEXT.md"
        assert ac_file.is_file()
        assert len(ac_file.read_text(encoding="utf-8").splitlines()) <= 60

        # Simulate next session startup: recover_session parses and provides plan
        plan, recovered_state = recover_session(tmpdir, apply_fix=True)
        assert recovered_state is not None
        assert recovered_state.mission_id == "M-SESSION-RECOVER"
        assert recovered_state.status == TaskStatus.ACTIVE
        assert "Resume" in plan.explanation or "service.py" in plan.explanation or plan.action == "RESUME_STAGE"


def test_scenario_f_verification_demotion_on_late_code_modification():
    """Scenario F: Modifying code after checker approval invalidates verdict and demotes state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)
        (Path(tmpdir) / "docs").mkdir()
        (Path(tmpdir) / "src").mkdir()

        code_file = Path(tmpdir) / "src" / "worker.py"
        code_file.write_text("# v1", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=tmpdir, capture_output=True)

        task = create_task("M-LATE-EDIT", TaskClass.FEATURE, RiskTier.HIGH)
        task.current_stage = TaskStage.VERIFY
        task.verification_verdict = {
            "status": "PASS",
            "summary": "All tests passed",
            "git_head": "initial_head",
            "manifest_fingerprint": "mf1",
        }
        task.verification_state = "VERIFIED"
        sync_to_active_context(task, tmpdir)

        # Later, Maker modifies code without re-verifying
        code_file.write_text("# v2 with new changes", encoding="utf-8")

        snapshot = capture_worktree_snapshot(tmpdir)
        contradictions = detect_state_contradictions(task, snapshot)
        types = [c.type for c in contradictions]
        assert ContradictionType.VERIFICATION_STALE_WORKING_TREE in types

        # Stop Gate must block completion
        config = AntiOSConfig(
            test_runners=[RunnerConfig(name="dummy", default_command=["python", "-c", "exit(0)"])],
            policies=PoliciesConfig(fail_closed=True, enforce_same_change_set=False, enforce_working_tree_cleanliness=False)
        )
        decision, reason = evaluate_stop_gate({"workspacePaths": [tmpdir]}, config=config)
        assert decision == "continue"
        assert "Verification invalidated" in reason


def test_scenario_g_multimember_scoped_vs_escalated_execution():
    """Scenario G: Monorepo leaf execution stays isolated; shared core triggers blast radius."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _init_git_repo(tmpdir)

        # Create 2 packages: @repo/utils and @repo/service (@repo/service depends on @repo/utils)
        u_dir = Path(tmpdir) / "packages" / "utils"
        s_dir = Path(tmpdir) / "packages" / "service"
        u_dir.mkdir(parents=True)
        s_dir.mkdir(parents=True)

        (u_dir / "package.json").write_text(json.dumps({"name": "@repo/utils", "scripts": {"test": "echo test utils"}}))
        (s_dir / "package.json").write_text(json.dumps({
            "name": "@repo/service",
            "dependencies": {"@repo/utils": "*"},
            "scripts": {"test": "echo test service"}
        }))
        (Path(tmpdir) / "package.json").write_text(json.dumps({
            "name": "root-repo",
            "workspaces": ["packages/*"]
        }))

        runners = [
            RunnerConfig(name="utils-runner", manifest="packages/utils/package.json", default_command=["echo", "utils"], cwd="packages/utils"),
            RunnerConfig(name="service-runner", manifest="packages/service/package.json", default_command=["echo", "service"], cwd="packages/service"),
        ]

        # 1. Leaf member edit: isolated to service-runner
        leaf_runners, _ = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/service/src/main.ts"]
        )
        assert len(leaf_runners) == 1
        assert leaf_runners[0].name == "service-runner"

        # 2. Shared core edit: blast radius includes both utils and service
        blast_runners, rationale = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/utils/src/string.ts"]
        )
        assert len(blast_runners) == 2
        assert "dependents" in rationale.lower()

        # 3. Release workflow override: forces full workspace verification regardless of touched files
        release_runners, rationale_rel = resolve_verification_scope(
            repo_root=tmpdir,
            test_runners=runners,
            touched_files=["packages/service/README.md"],
            workflow="RELEASE"
        )
        assert len(release_runners) == 2
        assert "workflow" in rationale_rel.lower()


def test_scenario_h_dead_end_memory_distillation():
    """Scenario H: Dead-End Memory records failure, normalizes signatures, and distills verified lessons."""
    raw1 = "ModuleNotFoundError: No module named 'jwt' at 0x7ffd9a12 in /app/auth.py:45 [uuid: 123e4567-e89b-12d3-a456-426614174000]"
    raw2 = "ModuleNotFoundError: No module named 'jwt' at 0x7fff0011 in /var/tmp/auth.py:89 [uuid: 987fcdeb-51a2-43f1-b876-543210987654]"
    sig1 = DeterministicLessonMatcher.normalize_signature(raw1)
    sig2 = DeterministicLessonMatcher.normalize_signature(raw2)
    assert sig1 == sig2
    assert DeterministicLessonMatcher.are_semantically_equivalent(raw1, raw2) is True

    cand = LessonRecord(
        lesson_id="L-AUTH-01",
        title="Missing JWT package",
        trigger_or_failure="ModuleNotFoundError: No module named 'jwt'",
        rule_or_action="Install pyjwt and update pyproject.toml dependencies",
        authority=KnowledgeAuthority.CANDIDATE,
    )

    task_evidence = [
        {
            "task_id": "T-1",
            "failure_pattern": "ModuleNotFoundError: No module named 'jwt'",
            "verdict": "PASS",
            "resolution": "Installed pyjwt",
            "category": "",
        },
        {
            "task_id": "T-2",
            "failure_pattern": "ModuleNotFoundError: No module named 'jwt'",
            "verdict": "PASS",
            "resolution": "Installed pyjwt",
            "category": "",
        }
    ]

    updated, result = LessonDistillationEngine.distill(
        lessons=[cand],
        task_evidence=task_evidence,
        min_recurrences=2
    )
    assert len(result.promoted_lessons) == 1
    promoted = result.promoted_lessons[0]
    assert promoted.lesson_id == "L-AUTH-01"
    assert promoted.authority in (KnowledgeAuthority.VALIDATED, KnowledgeAuthority.DURABLE)

    # Format and parse markdown roundtrip
    md = format_lessons(updated)
    parsed = parse_lessons(md)
    assert len(parsed) >= 1
    assert any(p.lesson_id == "L-AUTH-01" for p in parsed)
