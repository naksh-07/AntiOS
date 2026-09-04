"""Unit tests for AntiOS Capability Registry (Phase 31–33)."""

from __future__ import annotations

from framework.core.capability import (
    Capability,
    CapabilityScope,
    CapabilityType,
    RuleConflictStatus,
    RulePrecedence,
)
from framework.core.capability_registry import CapabilityRegistry, build_default_registry
from framework.core.lifecycle import TaskClass


def test_registry_register_and_get():
    reg = CapabilityRegistry()
    cap = Capability(
        capability_id="tool:custom-test",
        type=CapabilityType.TOOL,
        name="Custom Test Tool",
        purpose="Run specific custom tests",
        applies_to_subsystems=["auth"],
        applies_to_task_types=["BUG"],
    )
    reg.register(cap)
    retrieved = reg.get("tool:custom-test")
    assert retrieved is not None
    assert retrieved.name == "Custom Test Tool"


def test_registry_secondary_indexing_subsystem_and_task():
    reg = CapabilityRegistry()
    cap1 = Capability(
        capability_id="skill:auth-skill",
        type=CapabilityType.SKILL,
        name="Auth Skill",
        purpose="Auth handling",
        applies_to_subsystems=["auth"],
        applies_to_task_types=["FEATURE"],
    )
    cap2 = Capability(
        capability_id="skill:global-skill",
        type=CapabilityType.SKILL,
        name="Global Skill",
        purpose="Global handling",
        applies_to_subsystems=["*"],
        applies_to_task_types=["*"],
    )
    reg.register(cap1)
    reg.register(cap2)

    # By subsystem
    auth_caps = reg.find_by_subsystem("auth")
    assert len(auth_caps) == 2

    db_caps = reg.find_by_subsystem("database")
    assert len(db_caps) == 1
    assert db_caps[0].capability_id == "skill:global-skill"

    # By task type
    feat_caps = reg.find_by_task_type("FEATURE")
    assert len(feat_caps) == 2

    bug_caps = reg.find_by_task_type(TaskClass.BUG)
    assert len(bug_caps) == 1
    assert bug_caps[0].capability_id == "skill:global-skill"


def test_registry_overwrite_cleans_old_indices():
    reg = CapabilityRegistry()
    cap = Capability(
        capability_id="tool:movable",
        type=CapabilityType.TOOL,
        name="Movable",
        purpose="Move around",
        applies_to_subsystems=["old_sub"],
    )
    reg.register(cap)
    assert len(reg.find_by_subsystem("old_sub")) == 1

    cap_updated = Capability(
        capability_id="tool:movable",
        type=CapabilityType.TOOL,
        name="Movable",
        purpose="Move around",
        applies_to_subsystems=["new_sub"],
    )
    reg.register(cap_updated, overwrite=True)
    assert len(reg.find_by_subsystem("old_sub")) == 0
    assert len(reg.find_by_subsystem("new_sub")) == 1


def test_registry_rule_conflict_detection_and_precedence():
    reg = CapabilityRegistry()
    r_core = Capability(
        capability_id="rule:core-req-test",
        type=CapabilityType.RULE,
        name="Core Require Test",
        purpose="Must require test pass",
        metadata={"precedence": RulePrecedence.CORE_INVARIANT.value}
    )
    r_proj = Capability(
        capability_id="rule:proj-skip-test",
        type=CapabilityType.RULE,
        name="Project Skip Test",
        purpose="May skip test for speed",
        metadata={"precedence": RulePrecedence.PROJECT_GUIDANCE.value}
    )
    conflicts = reg.check_rule_conflicts([r_core, r_proj])
    assert len(conflicts) == 1
    assert conflicts[0]["winning_rule"] == "rule:core-req-test"
    assert conflicts[0]["winning_precedence"] == RulePrecedence.CORE_INVARIANT.value
    assert conflicts[0]["status"] == RuleConflictStatus.CONFLICT_DETECTED.value


def test_registry_build_default_contains_canonical_assets():
    reg = build_default_registry()
    assert reg.get("skill:antios-engineer") is not None
    assert reg.get("skill:antios-verifier") is not None
    assert reg.get("skill:antios-debug") is not None
    assert reg.get("skill:antios-adapt-project") is not None

    assert reg.get("workflow:feature") is not None
    assert reg.get("workflow:bug") is not None
    assert reg.get("workflow:refactor") is not None
    assert reg.get("workflow:documentation") is not None
    assert reg.get("workflow:release") is not None

    assert reg.get("rule:platform-hook-interception") is not None
    assert reg.get("rule:core-immutable") is not None
    assert reg.get("rule:stop-gate-ratchet") is not None
    assert reg.get("rule:shallow-depth-law") is not None

    assert reg.get("verifier:solo") is not None
    assert reg.get("verifier:maker-checker") is not None
    assert reg.get("specialist:core-engineer") is not None
    assert reg.get("specialist:independent-verifier") is not None

    assert reg.get("tool:navigate-repo") is not None
    assert reg.get("tool:audit-docs") is not None
