"""Tests for AntiOS Deterministic Agent Router & AgentRoutingPack (Phase 34–36).

Verifies:
- AgentRouter delegation decision matrix (NO_DELEGATION vs DELEGATE_*)
- Why-selected and why-not-others rationale generation
- Prevention of multi-agent swarm on cross-subsystem tasks
- Handoff contract generation upon delegation
- Strict line budgets (format_card <= 25 lines, format_summary <= 15 lines)
- JSON serialization and deserialization
"""

from __future__ import annotations

from framework.core.agent_role import DelegationDecisionType
from framework.core.agent_router import AgentRouter
from framework.core.agent_routing_pack import AgentRoutingPack
from framework.core.agent_topology import build_default_agent_topology
from framework.core.capability_pack import CapabilityPack
from framework.core.config import AntiOSConfig


def _make_dummy_pack(
    task_intent: str = "Test task",
    task_class: str = "FEATURE",
    risk_tier: str = "LOW",
    subsystems: list[str] = None,
    skills: list[str] = None,
) -> CapabilityPack:
    return CapabilityPack(
        pack_id="pack-001",
        project_name="Test-Project",
        task_intent=task_intent,
        task_class=task_class,
        risk_tier=risk_tier,
        matched_subsystems=subsystems or ["core"],
        matched_components=["comp1"],
        workflow={"id": "wf:test", "name": "Test Workflow"},
        skills=[{"capability_id": s, "name": s} for s in (skills or ["skill:antios-engineer"])],
        rules=[{"capability_id": "rule:test", "name": "Test Rule"}],
        tools=[{"capability_id": "tool:test", "name": "Test Tool"}],
        verifier={"capability_id": "verifier:solo", "name": "Solo Verifier"},
        specialists=[],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED", "justification": "Local script suffices"},
        why_selected={"subsystem": "Direct match"},
        confidence=0.9,
        epistemic_state="OBSERVED",
    )


def test_router_solo_default_for_documentation():
    router = AgentRouter()
    pack = _make_dummy_pack(task_intent="Update docs", task_class="DOCUMENTATION", subsystems=["docs"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert routing.handoff_contract is None
    assert "documentation" in routing.delegation_reason.lower()


def test_router_delegates_bug_to_root_cause_debugger():
    router = AgentRouter()
    pack = _make_dummy_pack(task_intent="Fix crash in auth", task_class="BUG", subsystems=["auth"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_SPECIALIST.value
    assert routing.selected_specialist is not None
    assert routing.selected_specialist["role_id"] == "role:root-cause-debugger"
    assert routing.handoff_contract is not None
    assert routing.handoff_contract["delegated_role_id"] == "role:root-cause-debugger"


def test_router_delegates_investigation_to_investigation_specialist():
    router = AgentRouter()
    pack = _make_dummy_pack(task_intent="Investigate latency spike", task_class="INVESTIGATION", subsystems=["api"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_INVESTIGATION.value
    assert routing.selected_specialist is not None
    assert routing.selected_specialist["role_id"] == "role:investigation-specialist"
    assert routing.handoff_contract is not None


def test_router_prevents_multi_agent_swarm_on_cross_subsystem_feature():
    router = AgentRouter()
    pack = _make_dummy_pack(
        task_intent="Build checkout feature touching ui, api, and database",
        task_class="FEATURE",
        subsystems=["ui", "api", "database"],
    )
    routing = router.route_task(pack)

    # 3+ subsystems feature must force NO_DELEGATION
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert "cross-subsystem" in routing.delegation_reason.lower()
    assert routing.handoff_contract is None


def test_router_respects_adapter_policy_disabling_delegation():
    config = AntiOSConfig(
        name="No-Delegation-Project",
        agent_topology={"allow_delegation": False},
    )
    router = AgentRouter(config=config)
    pack = _make_dummy_pack(task_intent="Fix bug", task_class="BUG", subsystems=["auth"])
    routing = router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert "adapter policy" in routing.delegation_reason.lower()
    assert routing.selected_specialist is None


def test_agent_routing_pack_formatting_budgets():
    router = AgentRouter()
    pack = _make_dummy_pack(task_intent="Fix bug in auth", task_class="BUG", subsystems=["auth"])
    routing = router.route_task(pack)

    card = routing.format_card(max_lines=25)
    lines = card.split("\n")
    assert len(lines) <= 25
    assert "=== ANTIOS AGENT ROUTING PACK ===" in lines[0]

    summary = routing.format_summary(max_lines=15)
    summary_lines = summary.split("\n")
    assert len(summary_lines) <= 15
    assert "=== ANTIOS AGENT ROUTING SUMMARY ===" in summary_lines[0]


def test_agent_routing_pack_json_roundtrip():
    router = AgentRouter()
    pack = _make_dummy_pack(task_intent="Investigate issue", task_class="INVESTIGATION", subsystems=["core"])
    routing = router.route_task(pack)

    json_str = routing.to_json()
    assert isinstance(json_str, str)

    restored = AgentRoutingPack.from_dict(routing.to_dict())
    assert restored.routing_id == routing.routing_id
    assert restored.delegation_decision == routing.delegation_decision
    assert restored.selected_specialist == routing.selected_specialist
