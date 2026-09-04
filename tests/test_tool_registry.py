"""Tests for framework.core.tool_registry — Deterministic Tool & Provider Registry."""

from framework.core.tool import (
    CostHint,
    ExecutionMode,
    LatencyHint,
    Locality,
    ProviderAvailability,
    ToolDefinition,
    ToolPolicyStatus,
    ToolTier,
)
from framework.core.provider import (
    ProviderDefinition,
    ProviderPolicyStatus,
    ProviderType,
)
from framework.core.tool_registry import ToolRegistry, build_default_tool_registry


def test_tool_registry_registration_and_indices():
    """Verify tool registration correctly updates all secondary indices."""
    registry = ToolRegistry(project_name="Test-Registry")
    tool = ToolDefinition(
        tool_id="tool:custom-test",
        name="Custom Test Tool",
        purpose="Runs custom unit test",
        tier=ToolTier.PROJECT,
        provider_id="provider:project-local",
        capability_ids=["test:custom", "test:run"],
        supported_task_types=["BUG", "FEATURE"],
        supported_subsystems=["auth", "billing"],
        execution_mode=ExecutionMode.SYNCHRONOUS,
        locality=Locality.LOCAL,
        availability=ProviderAvailability.AVAILABLE,
    )
    registry.register_tool(tool)

    assert registry.get_tool("tool:custom-test") == tool
    assert tool in registry.list_tools(tier=ToolTier.PROJECT)
    assert tool in registry.find_tools_by_capability("test:custom")
    assert tool in registry.find_tools_by_capability("test:run")
    assert tool in registry.find_tools_by_subsystem("auth")
    assert tool in registry.find_tools_by_task_type("BUG")


def test_tool_registry_overwrite_cleans_old_indices():
    """Re-registering with updated attributes must clean up old indices."""
    registry = ToolRegistry(project_name="Test-Registry")
    t1 = ToolDefinition(
        tool_id="tool:mutable",
        name="Mutable Tool v1",
        purpose="v1",
        tier=ToolTier.SCRIPT,
        provider_id="provider:p1",
        capability_ids=["cap:alpha"],
    )
    registry.register_tool(t1)
    assert t1 in registry.find_tools_by_capability("cap:alpha")

    t2 = ToolDefinition(
        tool_id="tool:mutable",
        name="Mutable Tool v2",
        purpose="v2",
        tier=ToolTier.NATIVE,
        provider_id="provider:p2",
        capability_ids=["cap:beta"],
    )
    registry.register_tool(t2, overwrite=True)

    # Old indices cleaned
    assert t1 not in registry.find_tools_by_capability("cap:alpha")
    assert t2 in registry.find_tools_by_capability("cap:beta")
    assert t2 in registry.list_tools(tier=ToolTier.NATIVE)
    assert t1 not in registry.list_tools(tier=ToolTier.SCRIPT)


def test_build_default_tool_registry():
    """Verify build_default_tool_registry registers standard tools and providers."""
    registry = build_default_tool_registry()

    # Verify key providers exist
    assert registry.get_provider("provider:antigravity-native") is not None
    assert registry.get_provider("provider:local-script") is not None
    assert registry.get_provider("provider:external-cli") is not None
    assert registry.get_provider("provider:chrome-devtools") is not None
    assert registry.get_provider("provider:github") is not None

    # Verify rejected providers exist but are disabled
    rej = registry.get_provider("provider:notion")
    assert rej is not None
    assert not rej.enabled
    assert rej.policy_status == ProviderPolicyStatus.REJECTED

    # Verify key tools exist
    assert registry.get_tool("tool:native-run-command") is not None
    assert registry.get_tool("tool:native-git-cli") is not None
    assert registry.get_tool("tool:navigate-repo") is not None
    assert registry.get_tool("tool:mcp-chrome-inspect") is not None


def test_adapter_config_disables_tools_safely():
    """Adapter can disable non-core tools, but cannot disable core protected tools."""
    mock_config = {
        "tools": {
            "disabled_tools": ["tool:project-linter", "tool:native-run-command"],
        }
    }
    registry = build_default_tool_registry(config=mock_config)

    # Project linter disabled
    linter = registry.get_tool("tool:project-linter")
    assert linter is not None
    assert not linter.enabled
    assert linter.policy_status == ToolPolicyStatus.RESTRICTED

    # Core native run-command cannot be disabled by adapter
    run_cmd = registry.get_tool("tool:native-run-command")
    assert run_cmd is not None
    assert run_cmd.enabled
    assert run_cmd.policy_status == ToolPolicyStatus.PERMITTED
