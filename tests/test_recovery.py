"""Tests for AntiOS Session Recovery, Contradiction Detection, and Verification Continuity.

Validates the guiding doctrine: REALITY > STALE STATE.
Tests state reconstruction, contradiction detection across all taxonomy types,
verification staleness invalidation, and partial state recovery.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskStatus,
    TaskState,
    create_task,
    sync_to_active_context,
    parse_active_context,
)
from framework.core.recovery import (
    ContradictionType,
    Contradiction,
    RecoveryPlan,
    detect_state_contradictions,
    generate_recovery_plan,
    is_verification_stale,
    reconstruct_session_state,
    recover_session,
)
from framework.core.worktree import WorktreeSnapshot


def test_is_verification_stale_working_tree_modification():
    """Modifying source files after verification must mark verification stale."""
    state = TaskState(
        mission_id="Task-1",
        verification_state="VERIFIED",
        verification_verdict={"status": "PASS", "summary": "All tests passed", "files_audited": ["src/main.py"]},
    )
    # Dirty files include a modified source file
    stale, reasons = is_verification_stale(state, ["src/main.py"])
    assert stale is True
    assert any("Working tree files modified" in r for r in reasons)


def test_is_verification_stale_active_context_only_does_not_invalidate():
    """Updating docs/ACTIVE_CONTEXT.md alone should not invalidate code verification."""
    state = TaskState(
        mission_id="Task-1",
        verification_state="VERIFIED",
        verification_verdict={"status": "PASS", "summary": "All tests passed"},
    )
    stale, reasons = is_verification_stale(state, ["docs/ACTIVE_CONTEXT.md"])
    assert stale is False
    assert len(reasons) == 0


def test_is_verification_stale_manifest_drift():
    """Manifest fingerprint drift after verification invalidates prior test pass."""
    state = TaskState(
        mission_id="Task-1",
        verification_state="VERIFIED",
        verification_verdict={"status": "PASS", "manifest_fingerprint": "hash_abc_123"},
    )
    stale, reasons = is_verification_stale(state, [], current_manifest_fingerprint="hash_xyz_789")
    assert stale is True
    assert any("fingerprint drift" in r for r in reasons)


def test_contradiction_file_state_missing_file():
    """Detects contradiction when ACTIVE_CONTEXT claims changed file that does not exist and is clean."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Ghost-File",
            current_stage=TaskStage.IMPLEMENT,
            changed_files=["src/non_existent.py"],
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=True, dirty_files=[])
        contradictions = detect_state_contradictions(state, snapshot)
        types = [c.type for c in contradictions]
        assert ContradictionType.FILE_STATE_CONTRADICTION in types
    finally:
        shutil.rmtree(temp_dir)


def test_contradiction_premature_completion():
    """Detects contradiction when task claims COMPLETE at HIGH risk without verified verdict."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Premature",
            risk_tier=RiskTier.HIGH,
            current_stage=TaskStage.COMPLETE,
            status=TaskStatus.COMPLETED,
            verification_verdict=None,
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=True, dirty_files=[])
        contradictions = detect_state_contradictions(state, snapshot)
        types = [c.type for c in contradictions]
        assert ContradictionType.PREMATURE_COMPLETION in types
    finally:
        shutil.rmtree(temp_dir)


def test_contradiction_dirty_tree_on_complete():
    """Detects contradiction when task claims COMPLETE but working tree contains dirty code."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Dirty-Complete",
            risk_tier=RiskTier.LOW,
            current_stage=TaskStage.COMPLETE,
            status=TaskStatus.COMPLETED,
            verification_verdict={"status": "PASS"},
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=False, dirty_files=["src/extra.py"])
        contradictions = detect_state_contradictions(state, snapshot)
        types = [c.type for c in contradictions]
        assert ContradictionType.VERIFICATION_STALE_WORKING_TREE in types
    finally:
        shutil.rmtree(temp_dir)


def test_recovery_plan_from_interrupted_task():
    """Recovers safely from INTERRUPTED state preserving modified worktree files."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Interrupted",
            current_stage=TaskStage.IMPLEMENT,
            status=TaskStatus.INTERRUPTED,
            changed_files=["src/feature.py"],
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=False, dirty_files=["src/feature.py"])
        plan = generate_recovery_plan(state, snapshot, [], [])
        assert plan.action == "RESUME_STAGE"
        assert plan.recommended_stage == TaskStage.IMPLEMENT
        assert plan.recommended_status == TaskStatus.ACTIVE
        assert "src/feature.py" in plan.preserved_work
    finally:
        shutil.rmtree(temp_dir)


def test_recovery_plan_from_blocked_task():
    """Recovers cleanly from BLOCKED state, identifying blockers."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Blocked",
            current_stage=TaskStage.PLAN,
            status=TaskStatus.BLOCKED,
            blockers=["Missing schema definition"],
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=True, dirty_files=[])
        plan = generate_recovery_plan(state, snapshot, [], [])
        assert plan.action == "UNBLOCK"
        assert plan.recommended_status == TaskStatus.BLOCKED
        assert "Missing schema definition" in plan.explanation
    finally:
        shutil.rmtree(temp_dir)


def test_recovery_plan_demotes_stale_verification():
    """Recovery plan demotes status to VERIFICATION_STALE and stage to VERIFY when invalidation occurs."""
    temp_dir = tempfile.mkdtemp()
    try:
        state = TaskState(
            mission_id="Task-Stale",
            current_stage=TaskStage.REVIEW,
            status=TaskStatus.ACTIVE,
            verification_state="VERIFIED",
            verification_verdict={"status": "PASS"},
        )
        snapshot = WorktreeSnapshot(repo_root=temp_dir, is_clean=False, dirty_files=["src/hotfix.py"])
        plan = generate_recovery_plan(
            state, snapshot, [], ["Working tree files modified after verification: src/hotfix.py"]
        )
        assert plan.action == "RE_VERIFY"
        assert plan.recommended_status == TaskStatus.VERIFICATION_STALE
        assert plan.recommended_stage == TaskStage.VERIFY
    finally:
        shutil.rmtree(temp_dir)


def test_recover_session_apply_fix_synchronizes_bounded_active_context():
    """recover_session with apply_fix=True updates state and writes bounded docs/ACTIVE_CONTEXT.md."""
    temp_dir = tempfile.mkdtemp()
    try:
        os.system(f'git init "{temp_dir}" >nul 2>&1' if os.name == "nt" else f'git init "{temp_dir}" >/dev/null 2>&1')
        # Set up a task state with stale verification
        state = create_task("Task-Auto-Recover", TaskClass.BUG, RiskTier.HIGH)
        state.current_stage = TaskStage.REVIEW
        state.verification_state = "VERIFIED"
        state.verification_verdict = {"status": "PASS", "summary": "Passed"}
        sync_to_active_context(state, temp_dir)

        # Create a modified file on disk
        src_file = os.path.join(temp_dir, "src", "bugfix.py")
        os.makedirs(os.path.dirname(src_file), exist_ok=True)
        with open(src_file, "w") as f:
            f.write("fix = True\n")

        plan, recovered_state = recover_session(temp_dir, apply_fix=True)
        assert plan.action == "RE_VERIFY"
        assert recovered_state.status == TaskStatus.VERIFICATION_STALE
        assert recovered_state.current_stage == TaskStage.VERIFY

        # Verify docs/ACTIVE_CONTEXT.md was written and adheres to <= 60 lines
        target_path = os.path.join(temp_dir, "docs", "ACTIVE_CONTEXT.md")
        assert os.path.isfile(target_path)
        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 60
        assert any("VERIFICATION_STALE" in line for line in lines)
    finally:
        shutil.rmtree(temp_dir)
