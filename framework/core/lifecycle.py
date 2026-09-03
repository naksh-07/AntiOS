"""AntiOS Task Lifecycle & State Engine.

Formalizes the 10-step lifecycle progression, state transitions, interruption/recovery,
and bounded synchronization with docs/ACTIVE_CONTEXT.md.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import os
import re
from typing import Any, Dict, List, Optional, Tuple


class TaskStage(str, Enum):
    INTAKE = "INTAKE"
    UNDERSTAND = "UNDERSTAND"
    INVESTIGATE = "INVESTIGATE"
    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    TEST = "TEST"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"
    CONSOLIDATE = "CONSOLIDATE"
    COMPLETE = "COMPLETE"


class TaskStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"
    COMPLETED = "COMPLETED"


class TaskClass(str, Enum):
    FEATURE = "FEATURE"
    BUG = "BUG"
    REFACTOR = "REFACTOR"
    INVESTIGATION = "INVESTIGATION"
    DOCUMENTATION = "DOCUMENTATION"
    RELEASE = "RELEASE"


class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


ORDERED_STAGES = [
    TaskStage.INTAKE,
    TaskStage.UNDERSTAND,
    TaskStage.INVESTIGATE,
    TaskStage.PLAN,
    TaskStage.IMPLEMENT,
    TaskStage.TEST,
    TaskStage.VERIFY,
    TaskStage.REVIEW,
    TaskStage.CONSOLIDATE,
    TaskStage.COMPLETE,
]


@dataclass
class TaskState:
    mission_id: str
    task_class: TaskClass = TaskClass.FEATURE
    risk_tier: RiskTier = RiskTier.MEDIUM
    current_stage: TaskStage = TaskStage.INTAKE
    status: TaskStatus = TaskStatus.ACTIVE
    active_checklist: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    dead_ends: List[str] = field(default_factory=list)
    verification_verdict: Optional[Dict[str, Any]] = None
    next_action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_task(
    mission_id: str,
    task_class: TaskClass = TaskClass.FEATURE,
    risk_tier: RiskTier = RiskTier.MEDIUM,
    checklist: Optional[List[str]] = None,
    next_action: str = ""
) -> TaskState:
    """Initializes a new task state at INTAKE stage."""
    return TaskState(
        mission_id=mission_id,
        task_class=task_class,
        risk_tier=risk_tier,
        current_stage=TaskStage.INTAKE,
        status=TaskStatus.ACTIVE,
        active_checklist=checklist or [],
        next_action=next_action or "Understand boundaries and constraints."
    )


def transition_stage(
    state: TaskState,
    target_stage: TaskStage,
    evidence: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str, TaskState]:
    """Transitions the task state to target_stage following deterministic rules.

    Returns:
        (success, message, updated_state)
    """
    if state.status == TaskStatus.FAILED:
        return False, "Cannot transition failed task. Must recover first.", state

    current_idx = ORDERED_STAGES.index(state.current_stage)
    target_idx = ORDERED_STAGES.index(target_stage)

    # 1. Forward single-step progression
    if target_idx == current_idx + 1:
        # Gate checks
        if target_stage == TaskStage.COMPLETE:
            # Requires verified evidence or passing verdict
            if state.risk_tier == RiskTier.HIGH and not state.verification_verdict:
                return False, "High-risk task requires verified verdict before COMPLETE.", state

        state.current_stage = target_stage
        state.status = TaskStatus.COMPLETED if target_stage == TaskStage.COMPLETE else TaskStatus.ACTIVE
        if evidence:
            state.metadata.update(evidence)
        return True, f"Transitioned to {target_stage.value}", state

    # 2. Backward transitions (Recovery / Re-attempt)
    if target_idx < current_idx:
        state.current_stage = target_stage
        state.status = TaskStatus.ACTIVE
        if evidence:
            state.metadata.update(evidence)
        return True, f"Reverted stage to {target_stage.value} for recovery/re-iteration", state

    # 3. Same stage (update)
    if target_idx == current_idx:
        if evidence:
            state.metadata.update(evidence)
        return True, f"Updated stage {target_stage.value}", state

    # 4. Disallowed multi-step skipping
    return False, f"Invalid stage transition: cannot jump from {state.current_stage.value} to {target_stage.value} (must follow progression)", state


def interrupt_task(state: TaskState, reason: str) -> TaskState:
    """Marks task as interrupted while preserving stage and state."""
    state.status = TaskStatus.INTERRUPTED
    if reason and reason not in state.blockers:
        state.blockers.append(reason)
    state.next_action = f"Resume from {state.current_stage.value}: {reason}"
    return state


def block_task(state: TaskState, reason: str) -> TaskState:
    """Marks task as blocked."""
    state.status = TaskStatus.BLOCKED
    if reason and reason not in state.blockers:
        state.blockers.append(reason)
    state.next_action = f"Unblock {state.current_stage.value}: {reason}"
    return state


def recover_task(state: TaskState, recovery_action: str) -> TaskState:
    """Recovers an interrupted or blocked task to ACTIVE."""
    state.status = TaskStatus.ACTIVE
    state.next_action = recovery_action
    return state


def fail_task(state: TaskState, reason: str) -> TaskState:
    """Marks task as failed and logs reason to dead ends."""
    state.status = TaskStatus.FAILED
    state.dead_ends.append(reason)
    state.next_action = f"Resolve failure in {state.current_stage.value}: {reason}"
    return state


def sync_to_active_context(state: TaskState, repo_root: str) -> str:
    """Serializes TaskState to docs/ACTIVE_CONTEXT.md adhering strictly to <= 60 lines budget."""
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    target_path = os.path.join(docs_dir, "ACTIVE_CONTEXT.md")

    checklist_lines = [f"- [{'x' if item.startswith('[x]') else ' '}] {item.replace('[x]', '').replace('[ ]', '').strip()}" for item in state.active_checklist[:10]]
    if not checklist_lines:
        checklist_lines = ["- [ ] Initial task execution"]

    blocker_lines = [f"- {b}" for b in state.blockers[:5]] if state.blockers else ["- None"]
    dead_end_lines = [f"- {d}" for d in state.dead_ends[:5]] if state.dead_ends else ["- None"]

    verdict_summary = "None"
    if state.verification_verdict:
        verdict_summary = f"{state.verification_verdict.get('status', 'UNKNOWN')} ({state.verification_verdict.get('summary', '')})"

    sep = chr(10)
    content = f"""# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: {state.mission_id}
**Class**: {state.task_class.value} | **Risk**: {state.risk_tier.value}
**Stage**: {state.current_stage.value} | **Status**: {state.status.value}

## 1. Active Checklist
{sep.join(checklist_lines)}

## 2. Blockers & Invariants
{sep.join(blocker_lines)}

## 3. Dead-End Memory
{sep.join(dead_end_lines)}

## 4. Verification Verdict
- {verdict_summary}

## 5. Next Immediate Action
{state.next_action or f"Execute {state.current_stage.value} stage."}
"""

    lines = content.strip().splitlines()
    if len(lines) > 60:
        content = sep.join(lines[:60]) + sep

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return target_path


def parse_active_context(repo_root: str) -> Optional[TaskState]:
    """Parses docs/ACTIVE_CONTEXT.md back into TaskState during session resumption."""
    target_path = os.path.join(repo_root, "docs", "ACTIVE_CONTEXT.md")
    if not os.path.isfile(target_path):
        return None

    try:
        with open(target_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

        mission_match = re.search(r"\*\*Mission\*\*:\s*([^\n]+)", text)
        mission_id = mission_match.group(1).strip() if mission_match else "Recovered-Mission"

        class_match = re.search(r"\*\*Class\*\*:\s*([A-Z_]+)", text)
        task_class = TaskClass(class_match.group(1).strip()) if class_match and class_match.group(1).strip() in TaskClass.__members__ else TaskClass.FEATURE

        risk_match = re.search(r"\*\*Risk\*\*:\s*([A-Z_]+)", text)
        risk_tier = RiskTier(risk_match.group(1).strip()) if risk_match and risk_match.group(1).strip() in RiskTier.__members__ else RiskTier.MEDIUM

        stage_match = re.search(r"\*\*Stage\*\*:\s*([A-Z_]+)", text)
        stage = TaskStage(stage_match.group(1).strip()) if stage_match and stage_match.group(1).strip() in TaskStage.__members__ else TaskStage.INTAKE

        status_match = re.search(r"\*\*Status\*\*:\s*([A-Z_]+)", text)
        status = TaskStatus(status_match.group(1).strip()) if status_match and status_match.group(1).strip() in TaskStatus.__members__ else TaskStatus.ACTIVE

        action_match = re.search(r"## 5\. Next Immediate Action\s*\n([^\n#]+)", text)
        next_action = action_match.group(1).strip() if action_match else ""

        return TaskState(
            mission_id=mission_id,
            task_class=task_class,
            risk_tier=risk_tier,
            current_stage=stage,
            status=status,
            next_action=next_action
        )
    except Exception:
        return None
