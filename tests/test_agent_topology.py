"""Tests for AntiOS Agent Topology Registry & Discovery Engine (Phase 34–36).

Verifies:
- AgentTopologyRegistry multi-key indexing (role type, subsystem, task type)
- Canonical core roles in build_default_agent_topology()
- Adapter project-local specialist loading from antios.config.json
- SpecialistDiscoveryEngine candidate generation without silent activation
"""

from __future__ import annotations

from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    EscalationPolicyType,
)
from framework.core.agent_topology import (
    AgentTopologyRegistry,
    build_default_agent_topology,
    SpecialistDiscoveryEngine,
)
from framework.core.capability import CapabilityScope
from framework.core.config import AntiOSConfig
from framework.core.subsystem import SubsystemDeclaration


def test_registry_register_and_lookup():
    reg = AgentTopologyRegistry(project_name="Test-Registry")

    role = AgentRole(
        role_id="role:custom-worker",
        name="Custom Worker",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="Custom task worker",
        applies_to_task_types=["FEATURE"],
        applies_to_subsystems=["analytics"],
    )
    reg.register(role)

    assert reg.get("role:custom-worker") == role
    assert len(reg.list_all()) == 1

    by_type = reg.find_by_type(AgentRoleType.SPECIALIST)
    assert len(by_type) == 1
    assert by_type[0].role_id == "role:custom-worker"

    by_sub = reg.find_by_subsystem("analytics")
    assert len(by_sub) == 1

    by_sub_other = reg.find_by_subsystem("database")
    assert len(by_sub_other) == 0

    by_task = reg.find_by_task_type("FEATURE")
    assert len(by_task) == 1


def test_registry_overwrite_cleans_old_indices():
    reg = AgentTopologyRegistry(project_name="Test-Registry")

    role_v1 = AgentRole(
        role_id="role:worker",
        name="Worker V1",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="V1",
        applies_to_task_types=["BUG"],
        applies_to_subsystems=["ui"],
    )
    reg.register(role_v1)
    assert len(reg.find_by_subsystem("ui")) == 1

    role_v2 = AgentRole(
        role_id="role:worker",
        name="Worker V2",
        role_type=AgentRoleType.SPECIALIST,
        responsibility="V2",
        applies_to_task_types=["FEATURE"],
        applies_to_subsystems=["backend"],
    )
    reg.register(role_v2, overwrite=True)

    assert len(reg.find_by_subsystem("ui")) == 0
    assert len(reg.find_by_subsystem("backend")) == 1
    assert len(reg.find_by_task_type("BUG")) == 0
    assert len(reg.find_by_task_type("FEATURE")) == 1


def test_build_default_agent_topology_canonical_roles():
    reg = build_default_agent_topology()

    # Verify primary
    primary = reg.get_primary_agent()
    assert primary.role_id == "role:primary-engineer"
    assert primary.role_type == AgentRoleType.PRIMARY
    assert primary.can_delegate is True
    assert primary.max_depth == 2

    # Verify root cause debugger
    debugger = reg.get("role:root-cause-debugger")
    assert debugger is not None
    assert debugger.role_type == AgentRoleType.SPECIALIST
    assert debugger.can_delegate is False
    assert debugger.is_applicable_to_task("BUG") is True

    # Verify independent verifier
    verifier = reg.get("role:independent-verifier")
    assert verifier is not None
    assert verifier.role_type == AgentRoleType.CHECKER
    assert verifier.can_delegate is False
    assert verifier.boundary.is_capability_allowed("tool:write_to_file") is False

    # Verify investigation specialist
    investigator = reg.get("role:investigation-specialist")
    assert investigator is not None
    assert investigator.role_type == AgentRoleType.SPECIALIST
    assert investigator.is_applicable_to_task("INVESTIGATION") is True
    assert investigator.boundary.is_capability_allowed("tool:replace_file_content") is False

    # Verify security reviewer
    sec_reviewer = reg.get("role:security-reviewer")
    assert sec_reviewer is not None
    assert sec_reviewer.is_applicable_to_subsystem("governance") is True


def test_adapter_topology_loading_and_invariant_enforcement():
    config = AntiOSConfig(
        name="Adapter-Topology-Test",
        agent_topology={
            "allow_delegation": True,
            "specialists": {
                "role:frontend-specialist": {
                    "name": "Frontend Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Frontend UI component authoring",
                    "applies_to_subsystems": ["ui", "frontend"],
                    "applies_to_task_types": ["FEATURE", "BUG"],
                    "allowed_capabilities": ["skill:frontend", "tool:pnpm-test"],
                    "required_capabilities": ["skill:frontend"],
                    "max_depth": 2,
                    "can_delegate": False,
                }
            }
        }
    )

    reg = build_default_agent_topology(config)
    spec = reg.get("role:frontend-specialist")
    assert spec is not None
    assert spec.name == "Frontend Specialist"
    assert spec.scope == CapabilityScope.PROJECT_LOCAL
    assert spec.is_applicable_to_subsystem("ui") is True
    assert spec.can_delegate is False
    # Core immutable override must be forbidden automatically
    assert spec.boundary.is_capability_allowed("rule:core-immutable:override") is False


def test_specialist_discovery_engine():
    subsystems = [
        SubsystemDeclaration.from_dict({
            "subsystem_id": "ui",
            "name": "UI Subsystem",
            "description": "Frontend UI",
            "area": "frontend",
            "root_paths": ["src/ui"],
            "covering_tests": ["tests/ui/test_btn.ts"],
            "test_commands": ["pnpm test"],
            "keywords": ["button", "modal", "ui"],
        }),
        SubsystemDeclaration.from_dict({
            "subsystem_id": "database",
            "name": "DB Subsystem",
            "description": "Database Storage",
            "area": "data",
            "root_paths": ["src/db"],
            "covering_tests": ["tests/db/test_db.py"],
            "test_commands": ["pytest"],
            "keywords": ["schema", "migration", "database"],
        }),
    ]

    candidates = SpecialistDiscoveryEngine.discover_candidates(subsystems)
    assert len(candidates) >= 2

    c_names = [c.suggested_name for c in candidates]
    assert "Frontend Specialist" in c_names
    assert "Database Specialist" in c_names

    for c in candidates:
        assert c.epistemic_state == "CANDIDATE"
        assert c.confidence < 1.0
