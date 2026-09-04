"""Golden Task Test Suite for AntiOS Project Capability Layer (Phase 31–33).

Executes the 6 canonical golden scenarios:
1. UI component change ("Change the login button")
2. Backend/API change ("Update user authentication endpoint")
3. Database/schema change ("Add migration for account balance table")
4. Documentation change ("Update architecture documentation in docs/architecture.md")
5. Bug investigation ("Investigate intermittent timeout in test_gate.py")
6. Cross-subsystem change ("Update payment service and notification emitter")
"""

from __future__ import annotations

from framework.core.capability_router import CapabilityRouter
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


def _setup_golden_router() -> CapabilityRouter:
    wayfinder = WayfindingEngine()

    wayfinder.register_subsystem(SubsystemDeclaration(
        subsystem_id="ui",
        name="UI Subsystem",
        description="Frontend components and layout",
        area="frontend",
        root_paths=["src/ui", "frontend/src"],
        entrypoints=["src/ui/index.ts"],
        authoritative_files=["src/ui/button.tsx"],
        covering_tests=["tests/ui/test_button.ts"],
        test_commands=["pnpm test tests/ui/test_button.ts"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Accessibility WCAG AA compliance", "Zero inline CSS"],
        protected_invariants=[],
        dependencies=["api"],
        consumers=[],
        documentation_paths=["docs/ui.md"],
        keywords=["button", "login", "modal", "ui", "frontend"],
    ))

    wayfinder.register_subsystem(SubsystemDeclaration(
        subsystem_id="api",
        name="API Service Subsystem",
        description="Backend REST endpoints and authentication routes",
        area="backend",
        root_paths=["src/api"],
        entrypoints=["src/api/server.py"],
        authoritative_files=["src/api/auth.py"],
        covering_tests=["tests/api/test_auth.py"],
        test_commands=["pytest tests/api/test_auth.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG", "REFACTOR"],
        governing_rules=["Authenticate all non-public endpoints", "Rate limit auth attempts"],
        protected_invariants=["src/api/secret_keys.py"],
        dependencies=["database"],
        consumers=["ui"],
        documentation_paths=["docs/api.md"],
        keywords=["auth", "endpoint", "api", "route", "token"],
    ))

    wayfinder.register_subsystem(SubsystemDeclaration(
        subsystem_id="database",
        name="Database & Schema Subsystem",
        description="Database migrations, SQLite storage, and data models",
        area="data",
        root_paths=["src/db", "migrations"],
        entrypoints=["src/db/connection.py"],
        authoritative_files=["src/db/schema.sql"],
        covering_tests=["tests/db/test_migrations.py"],
        test_commands=["pytest tests/db/test_migrations.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG", "REFACTOR"],
        governing_rules=["All schema migrations must be reversible", "Zero unindexed foreign keys"],
        protected_invariants=["migrations/0001_initial.sql"],
        dependencies=[],
        consumers=["api"],
        documentation_paths=["docs/database.md"],
        keywords=["schema", "database", "migration", "table", "sql"],
    ))

    wayfinder.register_subsystem(SubsystemDeclaration(
        subsystem_id="docs",
        name="Documentation & Specs",
        description="Project architectural specs and user documentation",
        area="docs",
        root_paths=["docs"],
        entrypoints=["docs/architecture.md"],
        authoritative_files=["docs/architecture.md"],
        covering_tests=[],
        test_commands=["python framework/scripts/tools/audit_docs.py --all"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["DOCUMENTATION"],
        governing_rules=["Zero broken markdown references", "Strict token budgets"],
        protected_invariants=[],
        dependencies=[],
        consumers=[],
        documentation_paths=["docs/architecture.md"],
        keywords=["documentation", "doc", "spec", "guide", "architecture"],
    ))

    return CapabilityRouter(wayfinding_engine=wayfinder, project_name="AntiOS-Golden-Suite")


def test_golden_task_1_ui_component_change():
    """Case 1: 'Change the login button'."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities("Change the login button")
    assert pack.task_class == "FEATURE"
    assert "ui" in pack.matched_subsystems
    assert pack.workflow["id"] == "workflow:feature"

    skill_ids = [s["capability_id"] for s in pack.skills]
    assert "skill:antios-engineer" in skill_ids
    assert "skill:antios-debug" not in skill_ids

    rule_names = [r["name"] for r in pack.rules]
    assert any("Core Self-Protection" in r or "Platform Hook" in r for r in rule_names)

    assert pack.verifier["metadata"]["verifier_type"] == "MAKER_CHECKER"
    assert pack.irrelevant_capabilities_filtered > 20
    assert pack.confidence >= 0.7


def test_golden_task_2_backend_api_change():
    """Case 2: 'Update user authentication endpoint'."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities("Update user authentication endpoint")
    assert pack.task_class == "FEATURE"
    assert "api" in pack.matched_subsystems
    assert pack.workflow["id"] == "workflow:feature"

    tool_purposes = [t["purpose"] for t in pack.tools]
    assert any("test" in p.lower() for p in tool_purposes)
    assert "verifier" in pack.why_selected


def test_golden_task_3_database_schema_change():
    """Case 3: 'Add migration for account balance table'."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities("Add migration for account balance table")
    assert "database" in pack.matched_subsystems
    assert pack.risk_tier == "HIGH"
    assert pack.verifier["metadata"]["verifier_type"] == "MAKER_CHECKER"
    assert "skill:antios-verifier" in [s["capability_id"] for s in pack.skills]


def test_golden_task_4_documentation_change():
    """Case 4: 'Update architecture documentation in docs/architecture.md'."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities("Update architecture documentation in docs/architecture.md", target_files=["docs/architecture.md"])
    assert pack.task_class == "DOCUMENTATION"
    assert pack.workflow["id"] == "workflow:documentation"
    assert pack.verifier["metadata"]["verifier_type"] == "SOLO_VERIFIER"
    assert "skill:antios-debug" not in [s["capability_id"] for s in pack.skills]
    assert "tool:audit-docs" in [t["capability_id"] for t in pack.tools]


def test_golden_task_5_bug_investigation():
    """Case 5: 'Investigate intermittent timeout in test_gate.py'."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities("Fix bug causing intermittent timeout in test_gate.py")
    assert pack.task_class == "BUG"
    assert pack.workflow["id"] == "workflow:bug"

    skill_ids = [s["capability_id"] for s in pack.skills]
    assert "skill:antios-debug" in skill_ids
    assert "skill:antios-engineer" in skill_ids

    spec_ids = [s["capability_id"] for s in pack.specialists]
    assert "specialist:root-cause-debugger" in spec_ids


def test_golden_task_6_cross_subsystem_change():
    """Case 6: 'Update payment service and notification emitter' (multi-subsystem touch)."""
    router = _setup_golden_router()
    pack = router.resolve_capabilities(
        "Update payment service and notification emitter",
        target_files=["src/ui/button.tsx", "src/api/auth.py"]
    )
    assert pack.task_class == "FEATURE"
    assert "ui" in pack.matched_subsystems
    assert "api" in pack.matched_subsystems
    assert len(pack.matched_subsystems) == 2
    assert pack.risk_tier in ("MEDIUM", "HIGH")
    assert pack.irrelevant_capabilities_filtered > 15
