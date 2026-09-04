"""Tests for framework.core.tool_policy — Tool Selection Policy & MCP Justification."""

from framework.core.tool import ProviderAvailability, ToolTier
from framework.core.tool_registry import build_default_tool_registry
from framework.core.tool_policy import (
    DeterministicToolSelector,
    MCPJustificationEngine,
    MCPJustificationReport,
)
from framework.core.agent_role import AgentCapabilityBoundary, AgentRole, AgentRoleType


def test_mcp_justification_answers_eight_questions():
    """MCP justification report must answer all 8 canonical architectural questions."""
    rep = MCPJustificationEngine.evaluate(
        task_intent="Inspect browser layout and computed DOM",
        capability_id="browser:dom-inspection",
    )
    assert isinstance(rep, MCPJustificationReport)
    # 1. Is MCP needed?
    assert rep.is_needed is True
    # 2. Which provider?
    assert rep.provider_id == "provider:chrome-devtools"
    # 3. Why?
    assert "live computed styles" in rep.why
    # 4. Is it permitted?
    assert rep.is_permitted is True
    # 5. What local alternatives exist?
    assert len(rep.local_alternatives) > 0
    # 6. Why are those alternatives insufficient?
    assert "Static HTML files do not reflect" in rep.why_insufficient
    # 7. What fallback exists?
    assert rep.fallback is not None
    # 8. What happens on unavailable?
    assert rep.on_unavailable == "FAIL_CLOSED"


def test_mcp_justification_local_git_beats_github_mcp():
    """Local Git operations strictly reject GitHub MCP in favor of local Git CLI."""
    rep = MCPJustificationEngine.evaluate(
        task_intent="Check git status and local working tree diff",
        capability_id="git:status",
    )
    assert rep.status == "NOT_NEEDED"
    assert rep.is_needed is False
    assert rep.is_permitted is False
    assert "tool:native-git-cli" in rep.local_alternatives
    assert "authoritative" in rep.why.lower()


def test_mcp_justification_rejected_provider():
    """Explicitly rejected MCPs (notion, postman, posthog, etc.) must return REJECTED."""
    for rej_intent in ["Query notion database", "Test API with postman", "Inspect posthog events"]:
        rep = MCPJustificationEngine.evaluate(
            task_intent=rej_intent,
            capability_id="external:telemetry",
        )
        assert rep.status == "REJECTED"
        assert rep.is_permitted is False
        assert rep.is_needed is False


def test_tool_selector_tier_preference_native_first():
    """Native tools must be selected over scripts, project tools, external, and MCP."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    # Capability 'git:status' is exposed by both tool:native-git-cli (NATIVE) and tool:external-git (EXTERNAL)
    res = selector.select_tool(
        task_intent="Check git status",
        capability_id="git:status",
    )
    assert res["selected_tool"].tool_id == "tool:native-git-cli"
    assert res["execution_tier"] == ToolTier.NATIVE
    assert res["authorization_status"] == "AUTHORIZED"


def test_tool_selector_tier_preference_script_over_mcp():
    """Local deterministic scripts beat MCP when local script satisfies requirement."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Audit documentation references in repository",
        capability_id="docs:audit",
    )
    assert res["selected_tool"].tool_id == "tool:audit-docs"
    assert res["execution_tier"] == ToolTier.SCRIPT
    assert res["mcp_report"].status == "NOT_NEEDED"


def test_tool_selector_agent_boundary_authorization_blocks_unauthorized_specialist():
    """Specialist boundary forbidding write tools blocks write execution."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    # Verifier specialist strictly forbids file writes
    read_only_boundary = AgentCapabilityBoundary(
        allowed_capabilities=["tool:view-file", "tool:navigate-repo", "skill:antios-verifier"],
        forbidden_capabilities=["tool:write-file", "tool:replace-file-content"],
    )
    verifier_role = AgentRole(
        role_id="role:independent-verifier",
        name="Independent Verifier",
        role_type=AgentRoleType.CHECKER,
        responsibility="Audit diffs and run tests",
        boundary=read_only_boundary,
        can_delegate=False,
    )

    res = selector.select_tool(
        task_intent="Modify payment handler logic",
        capability_id="tool:replace-file-content",
        agent_role=verifier_role,
        target_files=["src/payment.py"],
    )
    assert res["authorization_status"] == "BLOCKED"
    assert "Agent boundary violation" in res["authorization_reason"]


def test_tool_selector_blocks_specialist_mutating_protected_core_zones():
    """Specialists attempting to mutate framework/ or .agents/ are blocked by governance."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    specialist_role = AgentRole(
        role_id="role:ui-specialist",
        name="UI Specialist",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="Build UI components",
        boundary=AgentCapabilityBoundary(allowed_capabilities=["*"]),
        can_delegate=False,
    )

    res = selector.select_tool(
        task_intent="Refactor framework core hook",
        capability_id="tool:replace-file-content",
        agent_role=specialist_role,
        target_files=["framework/core/guard.py"],
    )
    assert res["authorization_status"] == "BLOCKED"
    assert "Constitutional Violation" in res["authorization_reason"]
