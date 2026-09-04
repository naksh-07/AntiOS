"""Unit tests for AntiOS Capability Models & Enums (Phase 31–33)."""

from __future__ import annotations

from framework.core.capability import (
    Capability,
    CapabilityScope,
    CapabilityType,
    MCPDecision,
    MCPStatus,
    RuleCapability,
    RuleConflictStatus,
    RulePrecedence,
    SpecialistCapability,
    VerifierType,
)
from framework.core.lifecycle import TaskClass


def test_capability_enums():
    assert CapabilityType.SKILL.value == "SKILL"
    assert CapabilityType.RULE.value == "RULE"
    assert CapabilityType.WORKFLOW.value == "WORKFLOW"
    assert CapabilityType.TOOL.value == "TOOL"
    assert CapabilityType.VERIFIER.value == "VERIFIER"
    assert CapabilityType.SPECIALIST.value == "SPECIALIST"
    assert CapabilityType.MCP_PROVIDER.value == "MCP_PROVIDER"

    assert CapabilityScope.CORE.value == "CORE"
    assert CapabilityScope.ADAPTER.value == "ADAPTER"
    assert CapabilityScope.PROJECT_LOCAL.value == "PROJECT_LOCAL"
    assert CapabilityScope.SUBSYSTEM.value == "SUBSYSTEM"


def test_rule_precedence_hierarchy():
    assert RulePrecedence.PLATFORM_HOOK.value < RulePrecedence.CORE_INVARIANT.value
    assert RulePrecedence.CORE_INVARIANT.value < RulePrecedence.ADAPTER_POLICY.value
    assert RulePrecedence.ADAPTER_POLICY.value < RulePrecedence.SUBSYSTEM_INVARIANT.value
    assert RulePrecedence.SUBSYSTEM_INVARIANT.value < RulePrecedence.PROJECT_GUIDANCE.value


def test_capability_creation_and_serialization():
    cap = Capability(
        capability_id="skill:test-engineer",
        type=CapabilityType.SKILL,
        name="Test Engineer Skill",
        purpose="Test procedural engineering policy",
        scope=CapabilityScope.CORE,
        applies_to_subsystems=["core", "api"],
        applies_to_task_types=["FEATURE", "BUG"],
        risk="MEDIUM",
        evidence="Unit test evidence",
    )

    d = cap.to_dict()
    assert d["capability_id"] == "skill:test-engineer"
    assert d["type"] == "SKILL"
    assert d["scope"] == "CORE"
    assert d["applies_to_subsystems"] == ["core", "api"]
    assert d["risk"] == "MEDIUM"

    reconstructed = Capability.from_dict(d)
    assert reconstructed.capability_id == cap.capability_id
    assert reconstructed.type == cap.type
    assert reconstructed.name == cap.name
    assert reconstructed.purpose == cap.purpose


def test_negative_applicability():
    cap = Capability(
        capability_id="skill:verifier-checker",
        type=CapabilityType.SKILL,
        name="Verifier Skill",
        purpose="Checker verification only",
        negative_applicability=["NOT_STAGE:IMPLEMENT", "NOT_ROLE:MAKER", "NOT_TASK:INVESTIGATION"]
    )

    assert cap.is_negatively_applicable({"stage": "IMPLEMENT", "role": "CHECKER", "task_class": "FEATURE"})
    assert cap.is_negatively_applicable({"stage": "PLAN", "role": "MAKER", "task_class": "FEATURE"})
    assert cap.is_negatively_applicable({"stage": "VERIFY", "role": "CHECKER", "task_class": "INVESTIGATION"})
    assert not cap.is_negatively_applicable({"stage": "VERIFY", "role": "CHECKER", "task_class": "FEATURE"})


def test_rule_capability_conversion():
    rc = RuleCapability(
        rule_id="stop-gate-test",
        name="Stop Gate Rule",
        statement="Physical tests must pass",
        precedence=RulePrecedence.CORE_INVARIANT,
        scope=CapabilityScope.CORE,
        rule_source="GATE",
    )
    cap = rc.to_capability()
    assert cap.capability_id == "rule:stop-gate-test"
    assert cap.type == CapabilityType.RULE
    assert cap.metadata["precedence"] == 2
    assert cap.metadata["precedence_name"] == "CORE_INVARIANT"


def test_specialist_capability_shallow_depth_law():
    sc = SpecialistCapability(
        role_id="independent-verifier",
        role_name="Independent Verifier",
        responsibility="Fresh context audit",
        scope=CapabilityScope.CORE,
        applicable_tasks=["FEATURE", "BUG"],
        applicable_subsystems=["*"],
        allowed_capabilities=["skill:antios-verifier"],
        required_verifier="verifier:maker-checker",
        escalation_path="Root Orchestrator",
        max_nesting_depth=2,
    )
    cap = sc.to_capability()
    assert cap.capability_id == "specialist:independent-verifier"
    assert cap.type == CapabilityType.SPECIALIST
    assert cap.metadata["max_nesting_depth"] == 2


def test_mcp_decision_serialization():
    decision = MCPDecision(
        provider_id="mcp:chrome-devtools",
        status=MCPStatus.USEFUL,
        justification="Browser layout inspection",
        is_permitted=True,
    )
    d = decision.to_dict()
    assert d["status"] == "USEFUL"
    assert d["is_permitted"] is True
