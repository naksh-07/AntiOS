"""Golden Tool & Provider Routing Test Suite (12 Canonical Scenarios).

Evaluates deterministic tool selection, tier ordering, MCP justification,
and authorization across all required AntiOS engineering scenarios.
"""

from framework.core.tool import ProviderAvailability, ToolTier
from framework.core.provider import ProviderDefinition, ProviderPolicyStatus, ProviderType
from framework.core.tool_registry import ToolRegistry, build_default_tool_registry
from framework.core.tool_policy import DeterministicToolSelector, MCPJustificationEngine


def test_golden_scenario_1_local_git_status():
    """Scenario 1: Local Git status -> Native Git CLI, NOT GitHub MCP."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Check git status and working tree cleanliness",
        capability_id="git:status",
    )
    assert res["selected_tool"].tool_id == "tool:native-git-cli"
    assert res["selected_provider"].provider_id == "provider:antigravity-native"
    assert res["execution_tier"] == ToolTier.NATIVE
    assert res["mcp_report"].status == "NOT_NEEDED"
    assert not res["mcp_report"].is_needed


def test_golden_scenario_2_local_file_inspection():
    """Scenario 2: Local file inspection -> Native view_file."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Inspect file contents of src/main.py",
        capability_id="file:read",
    )
    assert res["selected_tool"].tool_id == "tool:native-view-file"
    assert res["execution_tier"] == ToolTier.NATIVE
    assert res["mcp_report"].status == "NOT_NEEDED"


def test_golden_scenario_3_repository_navigation():
    """Scenario 3: Repository wayfinding -> Local navigate_repo script."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Locate owning subsystem and entrypoints for user auth",
        capability_id="wayfinding:subsystem",
    )
    assert res["selected_tool"].tool_id == "tool:navigate-repo"
    assert res["execution_tier"] == ToolTier.SCRIPT
    assert res["mcp_report"].status == "NOT_NEEDED"


def test_golden_scenario_4_browser_dom_inspection():
    """Scenario 4: Browser DOM inspection -> Chrome DevTools MCP justified."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Inspect browser DOM layout and computed accessibility tree",
        capability_id="browser:dom-inspection",
    )
    assert res["selected_tool"].tool_id == "tool:mcp-chrome-inspect"
    assert res["selected_provider"].provider_id == "provider:chrome-devtools"
    assert res["execution_tier"] == ToolTier.MCP
    assert res["mcp_report"].status == "USEFUL"
    assert res["mcp_report"].is_needed is True
    assert res["mcp_report"].is_permitted is True


def test_golden_scenario_5_browser_e2e_automation():
    """Scenario 5: Browser E2E automation -> Playwright MCP justified."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Execute headless browser click and assert flow with playwright",
        capability_id="browser:e2e-automation",
    )
    assert res["selected_tool"].tool_id == "tool:mcp-playwright-exec"
    assert res["selected_provider"].provider_id == "provider:playwright"
    assert res["execution_tier"] == ToolTier.MCP
    assert res["mcp_report"].status == "USEFUL"


def test_golden_scenario_6_github_remote_pr_operation():
    """Scenario 6: GitHub remote PR operation -> GitHub remote MCP permitted."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Create remote pull request for feature branch on github",
        capability_id="github:create-pull-request",
    )
    assert res["selected_tool"].tool_id == "tool:mcp-github-create-pr"
    assert res["selected_provider"].provider_id == "provider:github"
    assert res["execution_tier"] == ToolTier.MCP
    assert res["mcp_report"].status == "OPTIONAL"
    assert res["mcp_report"].is_permitted is True


def test_golden_scenario_7_upstream_api_docs_lookup():
    """Scenario 7: Upstream API docs lookup -> Gemini Docs MCP justified."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Search upstream google-genai documentation for gemini api docs",
        capability_id="docs:gemini-api-search",
    )
    assert res["selected_tool"].tool_id == "tool:mcp-gemini-search-docs"
    assert res["selected_provider"].provider_id == "provider:gemini-api-docs"
    assert res["execution_tier"] == ToolTier.MCP
    assert res["mcp_report"].status == "USEFUL"


def test_golden_scenario_8_unavailable_mcp_returns_unavailable():
    """Scenario 8: Unavailable MCP returns UNAVAILABLE without silent fallback."""
    registry = build_default_tool_registry()
    # Mark chrome-devtools provider as unavailable
    dev_prov = registry.get_provider("provider:chrome-devtools")
    dev_prov.availability = ProviderAvailability.UNAVAILABLE

    dev_tool = registry.get_tool("tool:mcp-chrome-inspect")
    dev_tool.availability = ProviderAvailability.UNAVAILABLE

    selector = DeterministicToolSelector(registry)
    res = selector.select_tool(
        task_intent="Inspect computed DOM layout in browser",
        capability_id="browser:dom-inspection",
    )
    assert res["mcp_report"].status == "UNAVAILABLE"
    assert res["availability"] == ProviderAvailability.UNAVAILABLE


def test_golden_scenario_9_rejected_mcp_permanently_rejected():
    """Scenario 9: Rejected MCP (e.g. Notion, Postman) strictly rejected."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Sync ticket details to notion database",
        capability_id="tool:mcp-notion",
    )
    assert res["mcp_report"].status == "REJECTED"
    assert not res["mcp_report"].is_permitted
    # Forbidden tool cannot be selected
    assert res["selected_tool"] is None or res["selected_tool"].tool_id != "tool:mcp-notion-api"


def test_golden_scenario_10_local_alternative_beats_mcp():
    """Scenario 10: Local alternative beats MCP (Local grep > Remote search MCP)."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    res = selector.select_tool(
        task_intent="Search codebase text patterns with grep",
        capability_id="search:grep",
    )
    assert res["selected_tool"].tool_id == "tool:native-grep-search"
    assert res["execution_tier"] == ToolTier.NATIVE
    assert res["mcp_report"].status == "NOT_NEEDED"


def test_golden_scenario_11_project_tool_beats_generic_external():
    """Scenario 11: Project-local tool beats generic external CLI."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    # Capability 'test:run' is exposed by project test runner
    res = selector.select_tool(
        task_intent="Run test suite for repository",
        capability_id="test:run",
    )
    assert res["selected_tool"].tool_id == "tool:project-test-runner"
    assert res["execution_tier"] == ToolTier.PROJECT


def test_golden_scenario_12_cross_subsystem_task_multi_mechanism():
    """Scenario 12: Cross-subsystem workflow requires separate capability tools."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    # Step 1: Navigating repo
    r1 = selector.select_tool("Navigate codebase", "wayfinding:subsystem")
    assert r1["selected_tool"].tool_id == "tool:navigate-repo"
    assert r1["execution_tier"] == ToolTier.SCRIPT

    # Step 2: Editing code
    r2 = selector.select_tool("Edit service code", "file:edit")
    assert r2["selected_tool"].tool_id == "tool:native-replace-content"
    assert r2["execution_tier"] == ToolTier.NATIVE

    # Step 3: Running test runner
    r3 = selector.select_tool("Execute unit tests", "test:run")
    assert r3["selected_tool"].tool_id == "tool:project-test-runner"
    assert r3["execution_tier"] == ToolTier.PROJECT

    # Step 4: Checking changeset
    r4 = selector.select_tool("Check same changeset integrity", "changeset:check")
    assert r4["selected_tool"].tool_id == "tool:check-changeset"
    assert r4["execution_tier"] == ToolTier.SCRIPT
