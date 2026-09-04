"""Tests for framework.core.tool_pack — Tool Routing Pack Data Model."""

import json
from framework.core.tool import ProviderAvailability, ToolTier
from framework.core.tool_pack import ToolRoutingPack


def test_tool_routing_pack_card_bounds():
    """format_card() must be strictly bounded <= 25 lines."""
    pack = ToolRoutingPack(
        pack_id="test-pack-001",
        task_intent="Check git status and working tree cleanliness",
        task_class="FEATURE",
        matched_subsystems=["core", "governance"],
        capability_id="git:status",
        agent_role_id="role:primary-engineer",
        selected_tool_id="tool:native-git-cli",
        selected_tool_name="Native Git CLI",
        selected_provider_id="provider:antigravity-native",
        execution_tier=ToolTier.NATIVE,
        why_selected="Selected Native Git CLI as highest-priority permitted mechanism",
        alternatives_considered=[{"tool_id": "tool:external-git", "tier": "EXTERNAL"}],
        why_alternatives_rejected=["tool:external-git: Lower tier than selected tool"],
        mcp_status="NOT_NEEDED",
        mcp_justification="Local Git CLI is authoritative, 100% offline, zero tokens",
        availability=ProviderAvailability.AVAILABLE,
        offline_mode=False,
        authorization_status="AUTHORIZED",
        evidence="ANTIOS_MCP_POLICY.md",
    )
    card = pack.format_card(max_lines=25)
    lines = card.split("\n")
    assert len(lines) <= 25
    assert "### [Tool Routing: test-pac]" in card
    assert "Native Git CLI" in card
    assert "NOT_NEEDED" in card


def test_tool_routing_pack_summary_bounds():
    """format_summary() must be strictly bounded <= 15 lines."""
    pack = ToolRoutingPack(
        pack_id="test-pack-002",
        task_intent="Inspect DOM layout",
        task_class="FEATURE",
        matched_subsystems=["ui"],
        capability_id="browser:dom-inspection",
        agent_role_id="role:ui-specialist",
        selected_tool_id="tool:mcp-chrome-inspect",
        selected_tool_name="Chrome DevTools DOM Inspector",
        selected_provider_id="provider:chrome-devtools",
        execution_tier=ToolTier.MCP,
        why_selected="Selected Chrome DevTools for computed layout inspection",
        mcp_status="USEFUL",
    )
    summary = pack.format_summary(max_lines=15)
    lines = summary.split("\n")
    assert len(lines) <= 15
    assert "Chrome DevTools DOM Inspector" in summary


def test_tool_routing_pack_json_roundtrip():
    """Verify complete JSON serialization and deserialization roundtrip."""
    pack = ToolRoutingPack(
        pack_id="test-pack-003",
        task_intent="Run project test runner",
        task_class="BUG",
        matched_subsystems=["testing"],
        capability_id="test:run",
        agent_role_id="role:root-cause-debugger",
        selected_tool_id="tool:project-test-runner",
        selected_tool_name="Project Test Runner",
        selected_provider_id="provider:project-local",
        execution_tier=ToolTier.PROJECT,
        why_selected="Project test runner executes local test suite",
        mcp_status="NOT_NEEDED",
        authorization_status="AUTHORIZED",
    )
    json_str = pack.to_json()
    data = json.loads(json_str)
    assert data["selected_tool_id"] == "tool:project-test-runner"
    assert data["execution_tier"] == "PROJECT"

    restored = ToolRoutingPack.from_dict(data)
    assert restored.pack_id == pack.pack_id
    assert restored.execution_tier == ToolTier.PROJECT
    assert restored.selected_tool_name == "Project Test Runner"
