"""Tests for framework.core.provider — Canonical Provider Abstraction."""

from framework.core.provider import (
    ProviderDefinition,
    ProviderPolicyStatus,
    ProviderType,
)
from framework.core.tool import Locality, ProviderAvailability


def test_provider_definition_roundtrip():
    """Verify ProviderDefinition serialization and deserialization."""
    prov = ProviderDefinition(
        provider_id="provider:test-prov",
        name="Test Provider",
        provider_type=ProviderType.PROJECT,
        capabilities=["test:run", "lint:run"],
        exposed_tools=["tool:test-runner"],
        locality=Locality.LOCAL,
        availability=ProviderAvailability.AVAILABLE,
        offline_capable=True,
        requires_network=False,
        permissions_required=["read"],
        policy_status=ProviderPolicyStatus.PERMITTED,
        allowed_tasks=["TEST", "LINT"],
        forbidden_tasks=["DEPLOY"],
        project_scope="workspace",
        justification="Local testing provider",
    )
    d = prov.to_dict()
    assert d["provider_id"] == "provider:test-prov"
    assert d["provider_type"] == "PROJECT"
    assert d["locality"] == "LOCAL"
    assert d["policy_status"] == "PERMITTED"

    restored = ProviderDefinition.from_dict(d)
    assert restored.provider_id == prov.provider_id
    assert restored.provider_type == ProviderType.PROJECT
    assert restored.capabilities == ["test:run", "lint:run"]
    assert restored.is_task_allowed("TEST")
    assert not restored.is_task_allowed("DEPLOY")


def test_provider_task_allow_and_forbidden_precedence():
    """Forbidden tasks must strictly override wildcards and allowed tasks."""
    prov = ProviderDefinition(
        provider_id="provider:test-wildcard",
        name="Wildcard Provider",
        provider_type=ProviderType.EXTERNAL,
        allowed_tasks=["*"],
        forbidden_tasks=["MUTATE_CORE", "OVERRIDE_GUARD"],
    )
    assert prov.is_task_allowed("FEATURE")
    assert prov.is_task_allowed("BUG")
    assert not prov.is_task_allowed("MUTATE_CORE")
    assert not prov.is_task_allowed("OVERRIDE_GUARD")


def test_provider_capability_exposure_matching():
    """Check capability exposure matching including wildcards."""
    prov = ProviderDefinition(
        provider_id="provider:git-cli",
        name="Git CLI Provider",
        provider_type=ProviderType.EXTERNAL,
        capabilities=["git:status", "git:diff", "git:log"],
    )
    assert prov.is_capability_exposed("git:status")
    assert prov.is_capability_exposed("git:diff")
    assert not prov.is_capability_exposed("browser:dom-inspection")


def test_rejected_provider_policy():
    """Rejected providers must carry REJECTED policy status and disabled state."""
    prov = ProviderDefinition(
        provider_id="provider:rejected-mcp",
        name="Rejected MCP Server",
        provider_type=ProviderType.MCP,
        availability=ProviderAvailability.POLICY_BLOCKED,
        policy_status=ProviderPolicyStatus.REJECTED,
        enabled=False,
        justification="REJECTED: Security violation",
    )
    assert prov.policy_status == ProviderPolicyStatus.REJECTED
    assert not prov.enabled
    assert prov.availability == ProviderAvailability.POLICY_BLOCKED
