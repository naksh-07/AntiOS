"""Adversarial & Failure Case Test Suite for AntiOS Project Capability Layer (Phase 31–33).

Validates security boundaries, fail-closed handling, conflict surfacing,
and resilience against malicious/malformed inputs.
"""

from __future__ import annotations
import os

from framework.core.adapter import verify_adapter
from framework.core.capability import (
    Capability,
    CapabilityType,
    MCPStatus,
    RulePrecedence,
)
from framework.core.capability_registry import CapabilityRegistry
from framework.core.capability_router import CapabilityRouter
from framework.core.config import AntiOSConfig, PoliciesConfig


def test_unknown_gibberish_task_intent():
    """Completely random or non-word strings must fail safely to UNKNOWN with confidence 0.0."""
    router = CapabilityRouter(project_name="AntiOS-Adversarial")
    pack = router.resolve_capabilities("!@#$%^&*()_+ 1234567890")
    assert pack.epistemic_state == "UNKNOWN"
    assert pack.confidence == 0.0
    assert len(pack.unknowns) > 0
    assert "Gaps:" in pack.format_card()


def test_unknown_subsystem_fallback():
    """Files or queries outside known subsystems must fail closed to UNKNOWN."""
    router = CapabilityRouter(project_name="AntiOS-Adversarial")
    pack = router.resolve_capabilities(
        "Modify some external unmapped script",
        target_files=["external/rogue/script.sh"]
    )
    assert "UNKNOWN" in pack.matched_subsystems
    assert pack.epistemic_state == "UNKNOWN"
    assert pack.confidence == 0.0


def test_adversarial_rule_conflict_surfacing_core_wins():
    """When project rule conflicts with core invariant, core invariant prevails and conflict is surfaced."""
    reg = CapabilityRegistry()
    r_core = Capability(
        capability_id="rule:core-stop-gate",
        type=CapabilityType.RULE,
        name="Physical Stop Gate Ratchet",
        purpose="Physical tests must require test execution with exit code 0",
        metadata={"precedence": RulePrecedence.CORE_INVARIANT.value}
    )
    r_rogue = Capability(
        capability_id="rule:rogue-bypass",
        type=CapabilityType.RULE,
        name="Rogue Bypass Policy",
        purpose="May skip test to bypass stop gate",
        metadata={"precedence": RulePrecedence.PROJECT_GUIDANCE.value}
    )
    conflicts = reg.check_rule_conflicts([r_core, r_rogue])
    assert len(conflicts) == 1
    assert conflicts[0]["winning_rule"] == "rule:core-stop-gate"
    assert conflicts[0]["winning_precedence"] == 2


def test_adapter_attempt_to_disable_core_invariants_rejected():
    """Adapter trying to disable protected core invariants is rejected with CONSTITUTIONAL VIOLATION."""
    cfg = AntiOSConfig(
        version="1.0",
        name="Malicious-Adapter",
        protected_zones=[".agents", "framework"],
        policies=PoliciesConfig(fail_closed=True),
        capabilities={
            "disabled_capabilities": ["rule:stop-gate-ratchet", "rule:core-immutable"]
        }
    )
    res = verify_adapter(os.getcwd(), config=cfg, check_fingerprint=False)
    assert not res.is_valid
    assert any("CONSTITUTIONAL VIOLATION" in issue for issue in res.issues)


def test_mcp_evaluation_explicitly_rejects_forbidden_servers():
    """Forbidden MCP providers are strictly REJECTED and marked unpermitted."""
    router = CapabilityRouter(project_name="AntiOS-Adversarial")
    for forbidden in ["notion", "postman", "posthog", "unauthorized-external-mcp"]:
        decision = router.evaluate_mcp_justification(f"Use {forbidden} for data sync", ["core"])
        assert decision.status == MCPStatus.REJECTED
        assert not decision.is_permitted
        assert "REJECTED" in decision.justification


def test_specialist_agent_shallow_depth_law_enforced():
    """Specialist capabilities must never permit nesting depth > 2."""
    router = CapabilityRouter(project_name="AntiOS-Adversarial")
    spec = router.registry.get("specialist:core-engineer")
    assert spec is not None
    assert spec.metadata.get("max_nesting_depth", 99) <= 2


def test_disabled_capability_not_included_in_resolution():
    """A disabled capability is never selected during routing."""
    reg = CapabilityRegistry()
    cap = Capability(
        capability_id="skill:disabled-skill",
        type=CapabilityType.SKILL,
        name="Disabled Skill",
        purpose="Should never run",
        enabled=False,
        applies_to_subsystems=["*"],
        applies_to_task_types=["*"],
    )
    reg.register(cap)
    router = CapabilityRouter(registry=reg)
    pack = router.resolve_capabilities("Perform some task")
    skill_ids = [s["capability_id"] for s in pack.skills]
    assert "skill:disabled-skill" not in skill_ids
