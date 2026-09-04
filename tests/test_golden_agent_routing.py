"""Golden Task Test Suite for AntiOS Agent Topology & Routing (Phase 34–36).

Executes the 10 canonical golden agent routing scenarios:
1. Simple UI change ("Change the login button")
2. Backend API change ("Update user authentication endpoint")
3. Database migration ("Add migration for account balance table")
4. Core governance change ("Refactor core security hook")
5. Documentation change ("Update architecture documentation in docs/architecture.md")
6. Cross-subsystem feature ("Update payment service and notification emitter")
7. Unknown domain ("Change random unknown component xyz")
8. High-risk task ("Modify Stop Gate ratchet logic")
9. Specialist unavailable (Requested domain specialist disabled)
10. Specialist scope mismatch (Specialist boundary forbids required capability)
"""

from __future__ import annotations

from framework.core.agent_role import (
    AgentRole,
    AgentRoleType,
    AgentCapabilityBoundary,
    DelegationDecisionType,
)
from framework.core.agent_router import AgentRouter
from framework.core.agent_topology import build_default_agent_topology
from framework.core.capability import CapabilityScope
from framework.core.capability_router import CapabilityRouter
from framework.core.config import AntiOSConfig
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


def _setup_golden_agent_router(config: AntiOSConfig = None) -> tuple[CapabilityRouter, AgentRouter]:
    wayfinder = WayfindingEngine()

    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "ui",
        "name": "UI Subsystem",
        "description": "Frontend components and layout",
        "area": "frontend",
        "root_paths": ["src/ui"],
        "authoritative_files": ["src/ui/button.tsx"],
        "covering_tests": ["tests/ui/test_button.ts"],
        "applicable_skills": ["antios-engineer"],
        "applicable_workflows": ["FEATURE", "BUG"],
        "keywords": ["button", "login", "modal", "ui", "frontend"],
    }))

    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "api",
        "name": "API Service Subsystem",
        "description": "Backend REST endpoints and authentication routes",
        "area": "backend",
        "root_paths": ["src/api"],
        "authoritative_files": ["src/api/auth.py"],
        "covering_tests": ["tests/api/test_auth.py"],
        "applicable_skills": ["antios-engineer"],
        "applicable_workflows": ["FEATURE", "BUG", "REFACTOR"],
        "keywords": ["auth", "endpoint", "api", "route", "token"],
    }))

    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "database",
        "name": "Database & Schema Subsystem",
        "description": "Database migrations, SQLite storage, and data models",
        "area": "data",
        "root_paths": ["src/db", "migrations"],
        "authoritative_files": ["src/db/schema.sql"],
        "covering_tests": ["tests/db/test_migrations.py"],
        "applicable_skills": ["antios-engineer"],
        "applicable_workflows": ["FEATURE", "BUG", "REFACTOR"],
        "keywords": ["schema", "database", "migration", "table", "sql"],
    }))

    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "docs",
        "name": "Documentation & Specs",
        "description": "Project architectural specs and user documentation",
        "area": "docs",
        "root_paths": ["docs"],
        "authoritative_files": ["docs/architecture.md"],
        "covering_tests": [],
        "applicable_skills": ["antios-engineer"],
        "applicable_workflows": ["DOCUMENTATION"],
        "keywords": ["documentation", "doc", "spec", "guide", "architecture"],
    }))

    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "governance",
        "name": "Core Governance & Hooks",
        "description": "AntiOS hooks, invariants, and pre-tool guards",
        "area": "core",
        "root_paths": ["framework/core", ".agents/hooks"],
        "authoritative_files": ["framework/core/guard.py"],
        "covering_tests": ["tests/test_guard_hardened.py"],
        "applicable_skills": ["antios-engineer"],
        "applicable_workflows": ["FEATURE", "BUG", "REFACTOR"],
        "keywords": ["hook", "governance", "security", "guard", "ratchet"],
    }))

    # Adapter with UI and Database specialist declarations
    default_config = config or AntiOSConfig(
        name="Golden-Agent-Project",
        agent_topology={
            "allow_delegation": True,
            "specialists": {
                "role:frontend-specialist": {
                    "name": "Frontend Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Frontend UI component authoring",
                    "applies_to_subsystems": ["ui"],
                    "applies_to_task_types": ["FEATURE", "BUG"],
                    "allowed_capabilities": ["skill:antios-engineer", "tool:navigate-repo", "rule:*"],
                    "forbidden_capabilities": ["rule:core-immutable:override"],
                    "max_depth": 2,
                    "can_delegate": False,
                },
                "role:database-specialist": {
                    "name": "Database Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Database migrations and schema engineering",
                    "applies_to_subsystems": ["database"],
                    "applies_to_task_types": ["FEATURE", "BUG", "REFACTOR"],
                    "allowed_capabilities": ["skill:antios-*", "tool:test-*", "rule:*"],
                    "forbidden_capabilities": ["rule:core-immutable:override"],
                    "max_depth": 2,
                    "can_delegate": False,
                }
            }
        }
    )

    cap_router = CapabilityRouter(wayfinding_engine=wayfinder, project_name="AntiOS-Golden-Agents")
    topology_reg = build_default_agent_topology(default_config)
    agent_router = AgentRouter(topology_registry=topology_reg, config=default_config, project_name="AntiOS-Golden-Agents")

    return cap_router, agent_router


def test_golden_scenario_1_simple_ui_change():
    """Scenario 1: Simple UI change ('Change the login button') -> UI Specialist."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Change the login button")
    routing = agent_router.route_task(pack)

    assert routing.task_class == "FEATURE"
    assert "ui" in routing.matched_subsystems
    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_SPECIALIST.value
    assert routing.selected_specialist is not None
    assert routing.selected_specialist["name"] == "Frontend Specialist"
    assert routing.handoff_contract is not None
    assert routing.required_verifier == "verifier:maker-checker"


def test_golden_scenario_2_backend_api_change():
    """Scenario 2: Backend API change ('Update user authentication endpoint')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Update user authentication endpoint")
    routing = agent_router.route_task(pack)

    assert routing.task_class == "FEATURE"
    assert "api" in routing.matched_subsystems
    # API specialist was not configured in adapter -> Primary Agent handles directly
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert routing.primary_role["role_id"] == "role:primary-engineer"


def test_golden_scenario_3_database_migration():
    """Scenario 3: Database migration ('Add migration for account balance table')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Add migration for account balance table")
    routing = agent_router.route_task(pack)

    assert "database" in routing.matched_subsystems
    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_SPECIALIST.value
    assert routing.selected_specialist["name"] == "Database Specialist"
    assert routing.required_verifier == "verifier:maker-checker"


def test_golden_scenario_4_core_governance_change():
    """Scenario 4: Core governance change ('Refactor core security hook')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Refactor core security hook", target_files=["framework/core/guard.py"])
    routing = agent_router.route_task(pack)

    assert "governance" in routing.matched_subsystems
    assert routing.delegation_decision == DelegationDecisionType.DELEGATE_SPECIALIST.value
    assert routing.selected_specialist["role_id"] == "role:security-reviewer"
    assert routing.required_verifier in ("verifier:independent-auditor", "verifier:maker-checker")


def test_golden_scenario_5_documentation_change():
    """Scenario 5: Documentation change ('Update architecture documentation in docs/architecture.md')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities(
        "Update architecture documentation in docs/architecture.md",
        target_files=["docs/architecture.md"]
    )
    routing = agent_router.route_task(pack)

    assert routing.task_class == "DOCUMENTATION"
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert routing.required_verifier == "verifier:solo"


def test_golden_scenario_6_cross_subsystem_feature():
    """Scenario 6: Cross-subsystem feature touching 3+ subsystems -> NO_DELEGATION (Prevent swarm)."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities(
        "Update payment service and notification emitter",
        target_files=["src/ui/button.tsx", "src/api/auth.py", "src/db/schema.sql"]
    )
    routing = agent_router.route_task(pack)

    assert len(routing.matched_subsystems) >= 3
    # Prevent swarm! Primary Agent must own cross-subsystem features directly
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert "cross-subsystem" in routing.delegation_reason.lower()


def test_golden_scenario_7_unknown_domain():
    """Scenario 7: Unknown domain ('Change random unknown component xyz')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Change random unknown component xyz")
    routing = agent_router.route_task(pack)

    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert "unknown" in routing.delegation_reason.lower()


def test_golden_scenario_8_high_risk_task():
    """Scenario 8: High-risk task ('Modify Stop Gate ratchet logic')."""
    cap_router, agent_router = _setup_golden_agent_router()
    pack = cap_router.resolve_capabilities("Modify Stop Gate ratchet logic", target_files=["framework/core/guard.py"])
    routing = agent_router.route_task(pack)

    assert routing.required_verifier in ("verifier:maker-checker", "verifier:independent-auditor")
    assert routing.primary_role["role_id"] == "role:primary-engineer"


def test_golden_scenario_9_specialist_unavailable():
    """Scenario 9: Specialist unavailable (Disabled in registry)."""
    cfg = AntiOSConfig(
        name="Disabled-Specialist-Project",
        agent_topology={
            "allow_delegation": True,
            "specialists": {
                "role:frontend-specialist": {
                    "name": "Frontend Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Frontend UI",
                    "applies_to_subsystems": ["ui"],
                    "enabled": False,  # EXPLICITLY DISABLED
                    "max_depth": 2,
                    "can_delegate": False,
                }
            }
        }
    )
    cap_router, agent_router = _setup_golden_agent_router(config=cfg)
    pack = cap_router.resolve_capabilities("Change the login button")
    routing = agent_router.route_task(pack)

    # Since specialist is disabled, fallback to Primary Agent
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert "Frontend Specialist" in routing.why_not_others
    assert "disabled" in routing.why_not_others["Frontend Specialist"].lower()


def test_golden_scenario_10_specialist_scope_mismatch():
    """Scenario 10: Specialist scope mismatch (Boundary forbids required capability)."""
    cfg = AntiOSConfig(
        name="Scope-Mismatch-Project",
        agent_topology={
            "allow_delegation": True,
            "specialists": {
                "role:frontend-specialist": {
                    "name": "Frontend Specialist",
                    "role_type": "SPECIALIST",
                    "responsibility": "Frontend UI",
                    "applies_to_subsystems": ["ui"],
                    "boundary": {
                        "allowed_capabilities": ["tool:pnpm"],
                        "forbidden_capabilities": ["skill:antios-engineer"],  # Forbids required skill!
                    },
                    "max_depth": 2,
                    "can_delegate": False,
                }
            }
        }
    )
    cap_router, agent_router = _setup_golden_agent_router(config=cfg)
    pack = cap_router.resolve_capabilities("Change the login button")
    routing = agent_router.route_task(pack)

    # Scope mismatch forces fallback to Primary Agent
    assert routing.delegation_decision == DelegationDecisionType.NO_DELEGATION.value
    assert routing.selected_specialist is None
    assert "scope mismatch" in routing.delegation_reason.lower()
