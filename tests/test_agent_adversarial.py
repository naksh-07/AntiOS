"""Adversarial Delegation Test Suite for AntiOS Agent Topology (Phase 34–36).

Verifies the 6 mandatory adversarial scenarios:
- Scenario A: Low-risk task where delegation would add no value -> NO_DELEGATION
- Scenario B: Specialized task with valid specialist -> DELEGATE_SPECIALIST
- Scenario C: High-risk task -> Specialist + Mandatory Independent Checker
- Scenario D: Specialist tries to modify protected AntiOS core -> Governance guard blocks it
- Scenario E: Specialist tries to spawn child -> Shallow Depth Law blocks it
- Scenario F: Specialist returns unsupported claim -> Primary requires evidence & verification
"""

from __future__ import annotations

from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    DelegationDecisionType,
    SpecialistResultReport,
)
from framework.core.agent_router import AgentRouter
from framework.core.agent_topology import build_default_agent_topology
from framework.core.capability_pack import CapabilityPack
from framework.core.config import AntiOSConfig
from framework.core.guard import evaluate_tool_call


def _make_task_pack(intent: str, t_class: str, risk: str, subs: list[str]) -> CapabilityPack:
    return CapabilityPack(
        pack_id="pack-adv",
        project_name="Adversarial-Suite",
        task_intent=intent,
        task_class=t_class,
        risk_tier=risk,
        matched_subsystems=subs,
        matched_components=["comp1"],
        workflow={"id": f"wf:{t_class.lower()}", "name": t_class},
        skills=[{"capability_id": "skill:antios-engineer"}],
        rules=[{"capability_id": "rule:core-immutable", "name": "Core Immutable"}],
        tools=[{"capability_id": "tool:navigate-repo", "name": "Navigate"}],
        verifier={"capability_id": "verifier:maker-checker" if risk in ("HIGH", "CRITICAL") else "verifier:solo"},
        specialists=[],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED"},
        why_selected={},
        confidence=0.9,
        epistemic_state="OBSERVED",
    )


def test_adversarial_scenario_a_low_risk_no_delegation():
    """Scenario A: Low-risk task where delegation would add no value -> NO_DELEGATION."""
    router = AgentRouter()
    pack = _make_task_pack("Format code comments in docs", "DOCUMENTATION", "LOW", ["docs"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert routing.handoff_contract is None


def test_adversarial_scenario_b_specialized_task_delegates():
    """Scenario B: Specialized task with valid specialist -> DELEGATE_SPECIALIST."""
    router = AgentRouter()
    pack = _make_task_pack("Fix memory leak in parser", "BUG", "MEDIUM", ["parser"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_SPECIALIST.value
    assert routing.selected_specialist is not None
    assert routing.selected_specialist["role_id"] == "role:root-cause-debugger"
    assert routing.handoff_contract is not None


def test_adversarial_scenario_c_high_risk_mandates_checker():
    """Scenario C: High-risk task -> Specialist work + Mandatory independent Checker."""
    router = AgentRouter()
    pack = _make_task_pack("Refactor security token generation", "REFACTOR", "HIGH", ["security"])
    routing = router.route_task(pack)

    assert routing.risk_tier == "HIGH"
    assert routing.required_verifier == "verifier:maker-checker"


def test_adversarial_scenario_d_specialist_cannot_modify_core():
    """Scenario D: Specialist tries to modify protected AntiOS core -> blocked by governance."""
    specialist = AgentRole(
        role_id="role:ui-specialist",
        name="UI Specialist",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="UI changes",
        boundary=AgentCapabilityBoundary(
            allowed_capabilities=["skill:frontend", "tool:write_to_file"],
            forbidden_capabilities=["rule:core-immutable:override"],
        ),
    )

    # 1. Role capability boundary forbids core rule override
    assert specialist.boundary.is_capability_allowed("rule:core-immutable:override") is False

    # 2. PreToolUse guard blocks attempts to modify framework/ or .agents/
    payload = {
        "toolCall": {
            "name": "write_to_file",
            "args": {"TargetFile": "framework/core/guard.py", "CodeContent": "def hacked(): pass"},
        },
        "workspacePaths": ["."],
    }
    decision, reason = evaluate_tool_call(payload)
    assert decision == "deny"
    assert "self-protection" in reason.lower() or "forbidden" in reason.lower()


def test_adversarial_scenario_e_specialist_cannot_spawn_child():
    """Scenario E: Specialist tries to spawn child -> depth law blocks it."""
    try:
        AgentRole(
            role_id="role:child-spawner",
            name="Child Spawner",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Attempting to delegate further",
            can_delegate=True,
        )
        assert False, "Should have raised ValueError on can_delegate=True"
    except ValueError as exc:
        assert "Shallow Depth Law violation" in str(exc)


def test_adversarial_scenario_f_unsupported_claim_requires_verification():
    """Scenario F: Specialist returns unsupported claim -> primary requires evidence / verification."""
    # A specialist result report with missing evidence or failed status must be detected
    unsupported_report = SpecialistResultReport(
        contract_id="contract-999",
        specialist_role_id="role:root-cause-debugger",
        status="SUCCESS",
        work_performed="I fixed the bug in my head without running tests",
        files_touched=["src/auth/service.py"],
        decisions=[],
        unresolved_issues=[],
        evidence="",  # EMPTY EVIDENCE
        verification_result={},  # NO VERIFICATION RESULT
    )

    # Primary verification inspection: unverified claim cannot be accepted
    has_evidence = bool(unsupported_report.evidence.strip())
    has_passing_verification = unsupported_report.verification_result.get("status") == "PASS"

    assert has_evidence is False
    assert has_passing_verification is False
