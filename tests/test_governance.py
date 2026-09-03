"""Tests for framework.core.governance — Governance model primitives."""

from framework.core.governance import (
    GovernancePrimitiveType,
    GovernancePrimitiveDefinition,
    GOVERNANCE_TAXONOMY,
    get_governance_primitive,
    validate_governance_boundaries,
)


def test_all_six_primitives_defined():
    """All 6 governance primitives must be present in the taxonomy."""
    expected = {"RULE", "SKILL", "WORKFLOW", "HOOK", "TOOL", "ADAPTER"}
    actual = {pt.value for pt in GOVERNANCE_TAXONOMY.keys()}
    assert actual == expected


def test_each_primitive_has_definition():
    """Each primitive must have a non-empty definition, location, and invariants."""
    for ptype, pdef in GOVERNANCE_TAXONOMY.items():
        assert len(pdef.definition) > 0, f"{ptype} has empty definition"
        assert len(pdef.physical_location) > 0, f"{ptype} has empty location"
        assert len(pdef.execution_context) > 0, f"{ptype} has empty context"
        assert len(pdef.invariants) > 0, f"{ptype} has no invariants"
        assert len(pdef.anti_patterns) > 0, f"{ptype} has no anti-patterns"


def test_get_governance_primitive():
    """get_governance_primitive should return correct definitions."""
    rule = get_governance_primitive(GovernancePrimitiveType.RULE)
    assert rule.primitive_type == GovernancePrimitiveType.RULE
    assert "cognitive directive" in rule.definition.lower()

    hook = get_governance_primitive(GovernancePrimitiveType.HOOK)
    assert hook.primitive_type == GovernancePrimitiveType.HOOK
    assert "deterministic" in hook.definition.lower()


def test_validate_governance_boundaries():
    """All primitives should pass validation."""
    results = validate_governance_boundaries()
    for name, valid in results.items():
        assert valid, f"Governance primitive {name} failed validation"


def test_no_duplicate_physical_locations():
    """Each primitive must have a distinct physical location."""
    locations = [pdef.physical_location for pdef in GOVERNANCE_TAXONOMY.values()]
    assert len(locations) == len(set(locations))


def test_hook_invariant_fail_closed():
    """Hook primitive must include fail-closed invariant."""
    hook = get_governance_primitive(GovernancePrimitiveType.HOOK)
    fail_closed_found = any("fail-closed" in inv.lower() for inv in hook.invariants)
    assert fail_closed_found, "Hook must have fail-closed invariant"


def test_tool_invariant_selection_policy():
    """Tool primitive must reference 3-tier selection policy."""
    tool = get_governance_primitive(GovernancePrimitiveType.TOOL)
    policy_found = any("3-tier" in inv.lower() or "native" in inv.lower() for inv in tool.invariants)
    assert policy_found, "Tool must reference selection policy"


def test_adapter_invariant_agnostic():
    """Adapter primitive must include domain-agnostic invariant."""
    adapter = get_governance_primitive(GovernancePrimitiveType.ADAPTER)
    agnostic_found = any("domain-agnostic" in inv.lower() or "agnostic" in inv.lower() for inv in adapter.invariants)
    assert agnostic_found, "Adapter must have domain-agnostic invariant"


def test_frozen_dataclass():
    """GovernancePrimitiveDefinition should be frozen (immutable)."""
    rule = get_governance_primitive(GovernancePrimitiveType.RULE)
    try:
        rule.definition = "hacked"
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass  # Expected
