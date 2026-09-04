"""Tests for AntiOS Agent Role Domain Models & Contracts (Phase 34–36).

Verifies:
- AgentRoleType, DelegationDecisionType, EscalationPolicyType enums
- AgentCapabilityBoundary wildcard, allowed, forbidden precedence
- AgentRole post_init validation and Shallow Depth Law invariants
- Serialization roundtrips (to_dict / from_dict)
- AgentHandoffContract and SpecialistResultReport schemas
"""

from __future__ import annotations

from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    DelegationDecisionType,
    EscalationPolicyType,
    AgentHandoffContract,
    SpecialistResultReport,
    SpecialistCandidate,
)
from framework.core.capability import CapabilityScope
from framework.core.lifecycle import TaskClass


def test_agent_role_enums():
    assert AgentRoleType.PRIMARY.value == "PRIMARY"
    assert AgentRoleType.SPECIALIST.value == "SPECIALIST"
    assert AgentRoleType.CHECKER.value == "CHECKER"
    assert AgentRoleType.CANDIDATE.value == "CANDIDATE"

    assert DelegationDecisionType.NO_DELEGATION.value == "NO_DELEGATION"
    assert DelegationDecisionType.DELEGATE_SPECIALIST.value == "DELEGATE_SPECIALIST"
    assert DelegationDecisionType.DELEGATE_MAKER_CHECKER.value == "DELEGATE_MAKER_CHECKER"
    assert DelegationDecisionType.DELEGATE_INVESTIGATION.value == "DELEGATE_INVESTIGATION"

    assert EscalationPolicyType.RETURN_TO_PRIMARY.value == "RETURN_TO_PRIMARY"
    assert EscalationPolicyType.FAIL_CLOSED.value == "FAIL_CLOSED"


def test_capability_boundary_wildcard_and_forbidden_precedence():
    boundary = AgentCapabilityBoundary(
        allowed_capabilities=["skill:*", "tool:navigate-repo"],
        forbidden_capabilities=["skill:forbidden-dangerous", "rule:core-immutable:override"],
        required_capabilities=["skill:antios-engineer"],
        inherited_capabilities=["rule:core-immutable"],
    )

    # Allowed by wildcard
    assert boundary.is_capability_allowed("skill:antios-engineer") is True
    assert boundary.is_capability_allowed("tool:navigate-repo") is True

    # Forbidden takes absolute precedence over wildcard
    assert boundary.is_capability_allowed("skill:forbidden-dangerous") is False
    assert boundary.is_capability_allowed("rule:core-immutable:override") is False

    # Inherited allowed
    assert boundary.is_capability_allowed("rule:core-immutable") is True

    # Not allowed
    assert boundary.is_capability_allowed("tool:arbitrary-shell") is False

    # Validation explanation
    valid, msg = boundary.validate_capability_access("skill:forbidden-dangerous")
    assert valid is False
    assert "FORBIDDEN" in msg

    valid, msg = boundary.validate_capability_access("tool:arbitrary-shell")
    assert valid is False
    assert "not in allowed" in msg


def test_shallow_depth_law_rejects_depth_greater_than_two():
    try:
        AgentRole(
            role_id="role:deep-agent",
            name="Deep Agent",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Invalid agent attempting depth 3",
            max_depth=3,
        )
        assert False, "Should have raised ValueError on max_depth > 2"
    except ValueError as e:
        assert "Shallow Depth Law violation" in str(e)


def test_shallow_depth_law_rejects_specialist_with_delegation_authority():
    try:
        AgentRole(
            role_id="role:rogue-specialist",
            name="Rogue Specialist",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Specialist attempting to spawn children",
            can_delegate=True,
        )
        assert False, "Should have raised ValueError on specialist with can_delegate=True"
    except ValueError as e:
        assert "Shallow Depth Law violation" in str(e)


def test_agent_role_serialization_roundtrip():
    role = AgentRole(
        role_id="role:test-ui-specialist",
        name="UI Specialist",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="Owns UI component implementation",
        scope=CapabilityScope.PROJECT_LOCAL,
        applies_to_task_types=["FEATURE", "BUG"],
        applies_to_subsystems=["ui", "frontend"],
        boundary=AgentCapabilityBoundary(
            allowed_capabilities=["skill:frontend", "tool:test-ui"],
            forbidden_capabilities=["rule:core-immutable:override"],
        ),
        required_verifier="verifier:maker-checker",
        escalation_policy=EscalationPolicyType.RETURN_TO_PRIMARY,
        max_depth=2,
        can_delegate=False,
        enabled=True,
        confidence=0.95,
        evidence="Declared in project profile",
        epistemic_state="OBSERVED",
        source="test_fixtures",
    )

    data = role.to_dict()
    assert data["role_id"] == "role:test-ui-specialist"
    assert data["role_type"] == "SPECIALIST"
    assert data["boundary"]["allowed_capabilities"] == ["skill:frontend", "tool:test-ui"]

    restored = AgentRole.from_dict(data)
    assert restored.role_id == role.role_id
    assert restored.role_type == AgentRoleType.SPECIALIST
    assert restored.boundary.is_capability_allowed("skill:frontend") is True
    assert restored.boundary.is_capability_allowed("rule:core-immutable:override") is False
    assert restored.is_applicable_to_subsystem("ui") is True
    assert restored.is_applicable_to_subsystem("backend") is False
    assert restored.is_applicable_to_task(TaskClass.FEATURE) is True
    assert restored.is_applicable_to_task(TaskClass.RELEASE) is False


def test_handoff_contract_and_report_serialization():
    contract = AgentHandoffContract(
        contract_id="contract-001",
        task="Implement login modal",
        target_files=["src/ui/login.tsx"],
        target_subsystems=["ui"],
        allowed_capabilities=["skill:frontend"],
        forbidden_capabilities=["rule:core-immutable:override"],
        constraints=["Shallow Depth Law <= 2"],
        expected_output="Clean diff with unit tests",
        verification_requirement="verifier:maker-checker",
        delegated_role_id="role:ui-specialist",
    )

    data = contract.to_dict()
    restored = AgentHandoffContract.from_dict(data)
    assert restored.contract_id == "contract-001"
    assert restored.target_files == ["src/ui/login.tsx"]

    report = SpecialistResultReport(
        contract_id="contract-001",
        specialist_role_id="role:ui-specialist",
        status="SUCCESS",
        work_performed="Implemented modal and passing tests",
        files_touched=["src/ui/login.tsx", "tests/ui/test_login.tsx"],
        decisions=["Used modal component from design system"],
        unresolved_issues=[],
        evidence="pnpm test exit code 0",
        verification_result={"status": "PASS"},
    )
    r_data = report.to_dict()
    assert r_data["status"] == "SUCCESS"
    assert len(r_data["files_touched"]) == 2


def test_specialist_candidate_lifecycle():
    candidate = SpecialistCandidate(
        candidate_id="candidate:database-specialist",
        suggested_name="Database Specialist",
        domain_subsystem="database",
        recurring_capabilities=["skill:antios-engineer", "tool:test-migrations"],
        rationale="Subsystem database has migrations and isolated tests",
        discovered_from="Subsystem 'database'",
        confidence=0.8,
        epistemic_state="CANDIDATE",
    )
    c_dict = candidate.to_dict()
    assert c_dict["epistemic_state"] == "CANDIDATE"
    assert c_dict["domain_subsystem"] == "database"
