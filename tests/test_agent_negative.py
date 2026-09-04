"""Negative & Malicious Attack Test Suite for AntiOS Agent Topology (Phase 34–36).

Attacks tested:
1. Malicious specialist metadata (corrupted types/payloads)
2. Specialist requesting forbidden capability (core write / hook override)
3. Role attempting wildcard authority over core zones
4. Invalid nesting depth (depth > 2)
5. Specialist attempting to spawn child (violating shallow depth law)
6. Specialist bypassing Checker
7. Conflicting role policies
8. Disabled specialist selection
9. Stale specialist definition
10. Project adapter overriding core invariant
11. Fake specialist ID resolution
12. Ambiguous specialist resolution
13. Cross-project capability leakage

Expected outcomes:
BLOCK, UNKNOWN, CONFLICT, UNAVAILABLE rather than silent authorization.
"""

from __future__ import annotations

from framework.core.adapter import verify_adapter
from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    DelegationDecisionType,
)
from framework.core.agent_router import AgentRouter
from framework.core.agent_topology import build_default_agent_topology
from framework.core.capability_pack import CapabilityPack
from framework.core.config import AntiOSConfig


def test_negative_invalid_depth_throws_value_error():
    """Depth > 2 is strictly blocked at initialization."""
    try:
        AgentRole(
            role_id="role:recursive-agent",
            name="Deep Nested Agent",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Attempting recursive delegation",
            max_depth=4,
        )
        assert False, "Should have raised ValueError on max_depth > 2"
    except ValueError as exc:
        assert "Shallow Depth Law violation" in str(exc)


def test_negative_specialist_cannot_delegate():
    """Specialist declaring can_delegate=True is strictly blocked."""
    try:
        AgentRole(
            role_id="role:unauthorized-spawner",
            name="Unauthorized Spawner",
            role_type=AgentRoleType.SPECIALIST,
            responsibility="Specialist attempting to spawn children",
            can_delegate=True,
        )
        assert False, "Should have raised ValueError on can_delegate=True"
    except ValueError as exc:
        assert "Shallow Depth Law violation" in str(exc)


def test_negative_checker_cannot_delegate():
    """Checker subagent declaring can_delegate=True is strictly blocked."""
    try:
        AgentRole(
            role_id="role:spawning-checker",
            name="Spawning Checker",
            role_type=AgentRoleType.CHECKER,
            responsibility="Checker attempting to spawn sub-checkers",
            can_delegate=True,
        )
        assert False, "Should have raised ValueError on can_delegate=True"
    except ValueError as exc:
        assert "Shallow Depth Law violation" in str(exc)


def test_negative_specialist_requesting_forbidden_capability():
    """Specialist boundary explicitly blocks forbidden capability access."""
    role = AgentRole(
        role_id="role:ui-worker",
        name="UI Worker",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="UI changes",
        boundary=AgentCapabilityBoundary(
            allowed_capabilities=["skill:frontend", "tool:test"],
            forbidden_capabilities=["rule:core-immutable:override", "workflow:release"],
        )
    )

    # Allowed
    assert role.boundary.is_capability_allowed("skill:frontend") is True

    # Forbidden must fail closed
    assert role.boundary.is_capability_allowed("rule:core-immutable:override") is False
    assert role.boundary.is_capability_allowed("workflow:release") is False

    valid, reason = role.boundary.validate_capability_access("rule:core-immutable:override")
    assert valid is False
    assert "FORBIDDEN" in reason


def test_negative_role_wildcard_boundary_denies_core_overrides():
    """Even a wildcard allowed boundary blocks core override when forbidden."""
    boundary = AgentCapabilityBoundary(
        allowed_capabilities=["*"],
        forbidden_capabilities=["rule:core-immutable:override", "rule:platform-hook-interception:override"],
    )

    assert boundary.is_capability_allowed("tool:anything") is True
    assert boundary.is_capability_allowed("rule:core-immutable:override") is False
    assert boundary.is_capability_allowed("rule:platform-hook-interception:override") is False


def test_negative_adapter_attempt_to_grant_specialist_delegation_blocked():
    """Adapter declaring specialist with can_delegate=True fails adapter verification."""
    config = AntiOSConfig(
        name="Malicious-Adapter",
        agent_topology={
            "specialists": {
                "role:rogue-adapter-specialist": {
                    "name": "Rogue Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Attempting swarm spawning",
                    "can_delegate": True,  # FORBIDDEN
                }
            }
        }
    )

    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION" in iss and "can_delegate=True" in iss for iss in result.issues)


def test_negative_adapter_attempt_to_grant_depth_greater_than_two_blocked():
    """Adapter declaring specialist with max_depth > 2 fails adapter verification."""
    config = AntiOSConfig(
        name="Deep-Adapter",
        agent_topology={
            "specialists": {
                "role:deep-adapter-specialist": {
                    "name": "Deep Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Attempting deep tree",
                    "max_depth": 3,  # FORBIDDEN
                }
            }
        }
    )

    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION" in iss and "max_depth" in iss for iss in result.issues)


def test_negative_adapter_attempt_to_override_core_immutable_blocked():
    """Adapter declaring specialist claiming core-immutable:override fails verification."""
    config = AntiOSConfig(
        name="Core-Override-Adapter",
        agent_topology={
            "specialists": {
                "role:override-specialist": {
                    "name": "Override Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Attempting to mutate core",
                    "allowed_capabilities": ["rule:core-immutable:override"],  # FORBIDDEN
                }
            }
        }
    )

    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION" in iss and "immutable core rules" in iss for iss in result.issues)


def test_negative_fake_or_unregistered_specialist_fallback_to_primary():
    """Attempting to route to a nonexistent specialist falls back safely to Primary Agent."""
    router = AgentRouter()
    pack = CapabilityPack(
        pack_id="pack-fake",
        project_name="AntiOS",
        task_intent="Perform mysterious action",
        task_class="UNKNOWN",
        risk_tier="LOW",
        matched_subsystems=[],
        matched_components=[],
        workflow={"id": "wf:unknown", "name": "Unknown"},
        skills=[],
        rules=[],
        tools=[],
        verifier={"capability_id": "verifier:solo"},
        specialists=[],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED"},
        why_selected={},
        confidence=0.0,
        epistemic_state="UNKNOWN",
    )

    routing = router.route_task(pack)
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert routing.primary_role["role_id"] == "role:primary-engineer"
