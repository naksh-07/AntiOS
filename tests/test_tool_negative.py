"""Adversarial & Security Test Suite for AntiOS Tool & Provider Layer.

Simulates capability spoofing, MCP escalation attacks, adapter policy violations,
and specialist boundary evasions.
"""

from framework.core.tool import (
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
from framework.core.tool_policy import DeterministicToolSelector, MCPJustificationEngine
from framework.core.agent_role import AgentCapabilityBoundary, AgentRole, AgentRoleType


def test_adversarial_mcp_pretending_to_be_native_rejected():
    """An external MCP cannot masquerade as NATIVE by declaring tier=NATIVE."""
    registry = build_default_tool_registry()
    # Malicious attempt: register an external server as NATIVE
    fake_native = ToolDefinition(
        tool_id="tool:rogue-mcp",
        name="Rogue MCP pretending to be Native",
        purpose="Bypass MCP policy",
        tier=ToolTier.NATIVE,
        provider_id="provider:notion",  # Backed by a rejected provider!
        capability_ids=["git:status"],
    )
    registry.register_tool(fake_native)

    selector = DeterministicToolSelector(registry)
    res = selector.select_tool(
        task_intent="Check git status",
        capability_id="git:status",
    )
    # The selector checks provider policy status; rejected provider cannot be selected!
    assert res["selected_tool"].tool_id != "tool:rogue-mcp"
    assert res["selected_tool"].tool_id == "tool:native-git-cli"


def test_adversarial_provider_claiming_unsupported_capability():
    """A provider claiming capabilities not allowed by policy is intercepted."""
    prov = ProviderDefinition(
        provider_id="provider:limited",
        name="Limited Provider",
        provider_type=ProviderType.EXTERNAL,
        capabilities=["read:logs"],
        forbidden_tasks=["*"],  # Forbids all tasks
    )
    assert not prov.is_task_allowed("FEATURE")
    assert not prov.is_task_allowed("BUG")


def test_adversarial_adapter_cannot_enable_rejected_mcp():
    """Project adapter attempting to enable rejected MCP is strictly ignored."""
    mock_config = {
        "tools": {
            "enabled_tools": ["tool:mcp-notion-api"],
            "custom_providers": [
                {"provider_id": "provider:notion", "enabled": True}
            ]
        }
    }
    registry = build_default_tool_registry(config=mock_config)
    notion_prov = registry.get_provider("provider:notion")
    assert not notion_prov.enabled
    assert notion_prov.policy_status == ProviderPolicyStatus.REJECTED


def test_adversarial_specialist_using_forbidden_write_tool_blocked():
    """Specialist agent with read-only boundary attempting to execute write tool is BLOCKED."""
    registry = build_default_tool_registry()
    selector = DeterministicToolSelector(registry)

    read_only_agent = AgentRole(
        role_id="role:investigation-specialist",
        name="Investigation Specialist",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="Investigate bug causes without mutating files",
        boundary=AgentCapabilityBoundary(
            allowed_capabilities=["tool:view-file", "tool:grep-search"],
            forbidden_capabilities=["tool:write-file", "tool:replace-file-content"],
        ),
        can_delegate=False,
    )

    res = selector.select_tool(
        task_intent="Overwrite production configuration",
        capability_id="tool:write-file",
        agent_role=read_only_agent,
    )
    assert res["authorization_status"] == "BLOCKED"
    assert "boundary violation" in res["authorization_reason"].lower()


def test_adversarial_local_git_routed_through_github_mcp_rejected():
    """Attempting to route local git status/diff through GitHub MCP is rejected."""
    rep = MCPJustificationEngine.evaluate(
        task_intent="Run git diff against HEAD via github mcp",
        capability_id="git:diff",
    )
    assert rep.status == "NOT_NEEDED"
    assert not rep.is_needed
    assert not rep.is_permitted
    assert "tool:native-git-cli" in rep.local_alternatives


def test_adversarial_credentials_in_metadata_detection():
    """Tool and provider definitions must not contain credential keys in metadata."""
    forbidden_credential_keys = ["api_key", "secret", "token", "password", "private_key"]
    registry = build_default_tool_registry()

    for tool in registry.list_tools(enabled_only=False):
        for k in tool.metadata.keys():
            assert not any(cred in k.lower() for cred in forbidden_credential_keys), f"Credential leaked in tool {tool.tool_id}: {k}"

    for prov in registry.list_providers(enabled_only=False):
        for k in prov.metadata.keys():
            assert not any(cred in k.lower() for cred in forbidden_credential_keys), f"Credential leaked in provider {prov.provider_id}: {k}"
