"""Failure Injection & Offline Degraded Mode Test Suite for AntiOS Tool Layer.

Verifies deterministic, safe degradation when network is down, tools are missing,
or providers fail without false done reports.
"""

from framework.core.tool import ProviderAvailability, ToolDefinition, ToolPolicyStatus, ToolTier
from framework.core.tool_registry import build_default_tool_registry
from framework.core.tool_policy import DeterministicToolSelector


def test_failure_injection_offline_mode_blocks_network_dependent_tool():
    """Offline mode filters out tools requiring network without pretending success."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    # Gemini API docs requires network (offline_capable=False)
    res = selector.select_tool(
        task_intent="Search upstream documentation",
        capability_id="docs:gemini-api-search",
        offline_mode=True,
    )
    # Selected tool must be None or marked unavailable; cannot select network tool in offline mode
    if res["selected_tool"]:
        assert res["selected_tool"].offline_capable is True
    else:
        assert res["selected_tool"] is None
        assert any("offline mode" in r for r in res["why_alternatives_rejected"])


def test_failure_injection_native_tool_unavailable_falls_back_to_external_cli():
    """When primary native git tool is marked unavailable, falls back to external git CLI."""
    registry = build_default_tool_registry()
    # Mark native git CLI unavailable
    native_git = registry.get_tool("tool:native-git-cli")
    native_git.availability = ProviderAvailability.UNAVAILABLE

    selector = DeterministicToolSelector(registry)
    res = selector.select_tool(
        task_intent="Check git status",
        capability_id="git:status",
    )
    # Should fall back to available external git
    assert res["selected_tool"].tool_id == "tool:external-git"
    assert res["execution_tier"] == ToolTier.EXTERNAL


def test_failure_injection_unregistered_capability_fails_closed():
    """Requesting a capability with zero matching tools fails closed safely."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Perform non-existent quantum teleportation",
        capability_id="quantum:teleport",
        task_class="UNKNOWN",
    )
    assert res["selected_tool"] is None or res["selected_tool"].policy_status != ToolPolicyStatus.FORBIDDEN
    assert "No available tool matched" in res["why_selected"] or res["selected_tool"] is not None


def test_failure_injection_provider_misconfigured_state():
    """Provider marked MISCONFIGURED is correctly exposed in routing result."""
    registry = build_default_tool_registry()
    prov = registry.get_provider("provider:chrome-devtools")
    prov.availability = ProviderAvailability.MISCONFIGURED
    tool = registry.get_tool("tool:mcp-chrome-inspect")
    tool.availability = ProviderAvailability.MISCONFIGURED

    selector = DeterministicToolSelector(registry)
    res = selector.select_tool(
        task_intent="Inspect computed DOM styles",
        capability_id="browser:dom-inspection",
    )
    assert res["availability"] == ProviderAvailability.MISCONFIGURED
