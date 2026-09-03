"""Tests for framework.core.lifecycle."""

import os
import tempfile

from framework.core.lifecycle import (
    RiskTier,
    TaskClass,
    TaskStage,
    TaskStatus,
    TaskState,
    create_task,
    transition_stage,
    interrupt_task,
    block_task,
    recover_task,
    fail_task,
    sync_to_active_context,
    parse_active_context,
    ORDERED_STAGES,
)


def test_lifecycle_initial_state():
    task = create_task("M-01", TaskClass.FEATURE, RiskTier.MEDIUM)
    assert task.mission_id == "M-01"
    assert task.task_class == TaskClass.FEATURE
    assert task.risk_tier == RiskTier.MEDIUM
    assert task.current_stage == TaskStage.INTAKE
    assert task.status == TaskStatus.ACTIVE


def test_lifecycle_forward_progression():
    task = create_task("M-02", TaskClass.FEATURE, RiskTier.LOW)

    for next_stage in ORDERED_STAGES[1:]:
        ok, msg, task = transition_stage(task, next_stage)
        assert ok is True, f"Failed transition to {next_stage}: {msg}"
        assert task.current_stage == next_stage

    assert task.status == TaskStatus.COMPLETED


def test_lifecycle_disallow_illegal_skips():
    task = create_task("M-03", TaskClass.FEATURE, RiskTier.MEDIUM)
    # Trying to jump from INTAKE directly to IMPLEMENT
    ok, msg, task = transition_stage(task, TaskStage.IMPLEMENT)
    assert ok is False
    assert "Invalid stage transition" in msg
    assert task.current_stage == TaskStage.INTAKE


def test_lifecycle_backward_transition_on_recovery():
    task = create_task("M-04", TaskClass.BUG, RiskTier.MEDIUM)
    # Advance to TEST
    for stage in [TaskStage.UNDERSTAND, TaskStage.INVESTIGATE, TaskStage.PLAN, TaskStage.IMPLEMENT, TaskStage.TEST]:
        transition_stage(task, stage)
    assert task.current_stage == TaskStage.TEST

    # On test failure, revert back to IMPLEMENT
    ok, msg, task = transition_stage(task, TaskStage.IMPLEMENT, evidence={"failure": "AssertionError"})
    assert ok is True
    assert task.current_stage == TaskStage.IMPLEMENT
    assert task.metadata.get("failure") == "AssertionError"


def test_lifecycle_high_risk_completion_gate():
    task = create_task("M-05", TaskClass.FEATURE, RiskTier.HIGH)
    for stage in ORDERED_STAGES[1:-1]:  # Up to CONSOLIDATE
        transition_stage(task, stage)
    assert task.current_stage == TaskStage.CONSOLIDATE

    # Attempt COMPLETE without verdict -> blocked
    ok, msg, task = transition_stage(task, TaskStage.COMPLETE)
    assert ok is False
    assert "High-risk task requires verified verdict" in msg

    # Provide verdict
    task.verification_verdict = {"status": "PASS", "summary": "Audit passed"}
    ok, msg, task = transition_stage(task, TaskStage.COMPLETE)
    assert ok is True
    assert task.current_stage == TaskStage.COMPLETE
    assert task.status == TaskStatus.COMPLETED


def test_lifecycle_interruption_and_recovery():
    task = create_task("M-06", TaskClass.REFACTOR, RiskTier.HIGH)
    interrupt_task(task, "User requested break")
    assert task.status == TaskStatus.INTERRUPTED
    assert "User requested break" in task.blockers

    recover_task(task, "Resuming work")
    assert task.status == TaskStatus.ACTIVE
    assert task.next_action == "Resuming work"


def test_lifecycle_sync_and_parse_active_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        task = create_task(
            mission_id="Phase-14-Test",
            task_class=TaskClass.FEATURE,
            risk_tier=RiskTier.HIGH,
            checklist=["[x] Design", "[ ] Code"],
            next_action="Implement feature logic"
        )
        task.current_stage = TaskStage.IMPLEMENT
        task.verification_verdict = {"status": "PASS", "summary": "All tests passed"}

        path = sync_to_active_context(task, tmpdir)
        assert os.path.isfile(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 60, f"ACTIVE_CONTEXT.md exceeded 60 lines: {len(lines)}"

        recovered = parse_active_context(tmpdir)
        assert recovered is not None
        assert recovered.mission_id == "Phase-14-Test"
        assert recovered.task_class == TaskClass.FEATURE
        assert recovered.risk_tier == RiskTier.HIGH
        assert recovered.current_stage == TaskStage.IMPLEMENT


def test_lifecycle_enhanced_statuses_and_fields():
    task = create_task(
        mission_id="Enhanced-Task-01",
        task_class=TaskClass.FEATURE,
        risk_tier=RiskTier.MEDIUM,
        target_member="antios-core",
        changed_files=["framework/core/memory.py", "framework/core/lifecycle.py"],
        verification_state="VERIFYING",
        pending_decisions=["DEC-09: Memory Model"],
    )
    assert task.status == TaskStatus.ACTIVE
    assert task.target_member == "antios-core"
    assert task.changed_files == ["framework/core/memory.py", "framework/core/lifecycle.py"]
    assert task.verification_state == "VERIFYING"
    assert task.pending_decisions == ["DEC-09: Memory Model"]

    task.status = TaskStatus.VERIFYING
    assert task.status == TaskStatus.VERIFYING

    task.status = TaskStatus.VERIFICATION_STALE
    assert task.status == TaskStatus.VERIFICATION_STALE


def test_lifecycle_enhanced_active_context_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        task = create_task(
            mission_id="Phase-16-Memory-Engine",
            task_class=TaskClass.FEATURE,
            risk_tier=RiskTier.HIGH,
            checklist=["[x] Formalize MemoryCategory", "[ ] Add verification"],
            next_action="Run full test suite",
            target_member="antios-memory",
            changed_files=["framework/core/memory.py", "framework/core/lifecycle.py"],
            verification_state="VERIFIED",
            pending_decisions=["DEC-10: Persistent Memory"],
        )
        task.current_stage = TaskStage.VERIFY
        task.verification_verdict = {"status": "PASS", "summary": "Memory model verified"}

        path = sync_to_active_context(task, tmpdir)
        assert os.path.isfile(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 60, f"Exceeded line budget: {len(lines)}"

        recovered = parse_active_context(tmpdir)
        assert recovered is not None
        assert recovered.mission_id == "Phase-16-Memory-Engine"
        assert recovered.task_class == TaskClass.FEATURE
        assert recovered.risk_tier == RiskTier.HIGH
        assert recovered.current_stage == TaskStage.VERIFY
        assert recovered.target_member == "antios-memory"
        assert recovered.verification_state == "VERIFIED"
        assert "framework/core/memory.py" in recovered.changed_files
        assert "framework/core/lifecycle.py" in recovered.changed_files
        assert "DEC-10: Persistent Memory" in recovered.pending_decisions
        assert recovered.verification_verdict is not None
        assert recovered.verification_verdict["status"] == "PASS"


def test_lifecycle_active_context_hard_budget_truncation():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a task with lots of checklist items, blockers, dead ends, and files
        huge_checklist = [f"[ ] Step {i}" for i in range(100)]
        huge_blockers = [f"Blocker {i}" for i in range(50)]
        huge_dead_ends = [f"Dead end {i}" for i in range(50)]
        huge_files = [f"path/to/file_{i}.py" for i in range(50)]

        task = create_task(
            mission_id="Budget-Stress-Test",
            checklist=huge_checklist,
            changed_files=huge_files,
            target_member="stress-tester",
        )
        task.blockers = huge_blockers
        task.dead_ends = huge_dead_ends

        path = sync_to_active_context(task, tmpdir)
        assert os.path.isfile(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) <= 60, f"Hard budget violated: {len(lines)} lines"

