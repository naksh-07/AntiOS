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
