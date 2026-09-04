"""Unit tests for AntiOS Phase 28-30 Canonical Knowledge Model & Relationship Graph."""

import os
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import (
    KnowledgeEpistemicTier,
    RelationshipType,
    KnowledgeEdge,
    KnowledgeGraph,
)


def _build_test_subsystems():
    db_decl = SubsystemDeclaration(
        subsystem_id="database",
        name="Database Engine",
        description="Persistent relational and key-value store access.",
        area="infra",
        root_paths=["src/db"],
        entrypoints=["src/db/connection.py"],
        authoritative_files=["src/db/connection.py", "src/db/schema.py"],
        covering_tests=["tests/test_db.py"],
        test_commands=["pytest tests/test_db.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["All transactions must be idempotent"],
        protected_invariants=["src/db/migrations"],
        dependencies=[],
        consumers=["auth", "billing"],
        documentation_paths=["docs/subsystems/database.md"],
        keywords=["db", "sql", "postgres", "storage"],
        purpose="Low-level storage abstraction",
        risk_tier="HIGH",
        owner="@infra-team",
        owner_source="CODEOWNERS",
        owner_confidence=0.95,
        epistemic_state="OBSERVED",
    )

    auth_decl = SubsystemDeclaration(
        subsystem_id="auth",
        name="Authentication Subsystem",
        description="Handles user identity, JWT tokens, and session persistence.",
        area="security",
        root_paths=["src/auth"],
        entrypoints=["src/auth/service.py"],
        authoritative_files=["src/auth/service.py"],
        covering_tests=["tests/test_auth.py"],
        test_commands=["pytest tests/test_auth.py"],
        applicable_skills=["antios-engineer", "antios-debug"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Never log secret keys"],
        protected_invariants=["src/auth/keys.py"],
        dependencies=["database"],
        consumers=["api-gateway", "billing"],
        documentation_paths=["docs/subsystems/auth.md"],
        keywords=["auth", "login", "jwt"],
        purpose="User identity and authorization",
        risk_tier="HIGH",
        owner="@security-team",
        owner_source="CODEOWNERS",
        owner_confidence=0.95,
        epistemic_state="OBSERVED",
    )

    billing_decl = SubsystemDeclaration(
        subsystem_id="billing",
        name="Billing Engine",
        description="Subscription billing and payment invoicing.",
        area="finance",
        root_paths=["src/billing"],
        entrypoints=["src/billing/service.py"],
        authoritative_files=["src/billing/service.py"],
        covering_tests=["tests/test_billing.py"],
        test_commands=["pytest tests/test_billing.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=["Strict webhook signature validation"],
        protected_invariants=[],
        dependencies=["auth", "database"],
        consumers=["reports"],
        documentation_paths=["docs/subsystems/billing.md"],
        keywords=["billing", "payment", "invoice"],
        purpose="Processes financial transactions",
        risk_tier="MEDIUM",
        owner="@finance-team",
        owner_source="MANIFEST",
        owner_confidence=0.80,
        epistemic_state="INFERRED",
    )

    reports_decl = SubsystemDeclaration(
        subsystem_id="reports",
        name="Reporting Service",
        description="Aggregates periodic financial summaries.",
        area="analytics",
        root_paths=["src/reports"],
        entrypoints=["src/reports/engine.py"],
        authoritative_files=["src/reports/engine.py"],
        covering_tests=["tests/test_reports.py"],
        test_commands=["pytest tests/test_reports.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=[],
        protected_invariants=[],
        dependencies=["billing"],
        consumers=[],
        documentation_paths=[],
        keywords=["reports", "analytics"],
        purpose="Assembles reporting metrics",
        risk_tier="LOW",
        owner=None,
        owner_source="UNKNOWN",
        owner_confidence=0.0,
        epistemic_state="INFERRED",
    )

    return [db_decl, auth_decl, billing_decl, reports_decl]


def test_knowledge_graph_registration_and_typed_edges():
    graph = KnowledgeGraph()
    subs = _build_test_subsystems()
    for s in subs:
        graph.add_component(s)

    assert len(graph.list_components()) == 4
    auth = graph.get_component("auth")
    assert auth is not None
    assert auth.name == "Authentication Subsystem"

    # Test DEPENDS_ON relationship
    auth_deps = graph.get_dependencies("auth", transitive=False)
    assert "database" in auth_deps

    # Test TESTED_BY relationship
    test_edges = graph.get_related("auth", RelationshipType.TESTED_BY, direction="forward")
    assert len(test_edges) == 1
    assert test_edges[0].target == "tests/test_auth.py"

    # Test GOVERNED_BY relationship
    rule_edges = graph.get_related("auth", RelationshipType.GOVERNED_BY, direction="forward")
    assert any("secret keys" in e.target for e in rule_edges)

    # Test REQUIRES_SKILL relationship
    skill_edges = graph.get_related("auth", RelationshipType.REQUIRES_SKILL, direction="forward")
    skills = [e.target for e in skill_edges]
    assert "antios-engineer" in skills
    assert "antios-debug" in skills


def test_transitive_dependencies_resolution():
    graph = KnowledgeGraph()
    for s in _build_test_subsystems():
        graph.add_component(s)

    # reports depends on billing, billing depends on auth and database, auth depends on database
    trans_deps = graph.get_dependencies("reports", transitive=True)
    assert "billing" in trans_deps
    assert "auth" in trans_deps
    assert "database" in trans_deps


def test_transitive_consumers_blast_radius():
    graph = KnowledgeGraph()
    for s in _build_test_subsystems():
        graph.add_component(s)

    # Modifying database affects auth and billing directly, and reports transitively
    db_consumers = graph.get_consumers("database", transitive=True)
    assert "auth" in db_consumers
    assert "billing" in db_consumers
    assert "reports" in db_consumers

    # Leaf component has 0 consumers
    reports_consumers = graph.get_consumers("reports", transitive=True)
    assert reports_consumers == []


def test_blast_radius_calculation_and_risk_scoring():
    graph = KnowledgeGraph()
    for s in _build_test_subsystems():
        graph.add_component(s)

    blast_db = graph.calculate_blast_radius("database")
    assert blast_db["risk_tier"] == "HIGH"
    assert "auth" in blast_db["direct_consumers"]
    assert "reports" in blast_db["transitive_consumers"]
    assert "tests/test_db.py" in blast_db["affected_tests"]
    assert "tests/test_reports.py" in blast_db["affected_tests"]
    assert "HIGH:" in blast_db["blast_radius_summary"]

    blast_reports = graph.calculate_blast_radius("reports")
    assert blast_reports["risk_tier"] == "LOW"
    assert blast_reports["transitive_consumers"] == []
    assert "Leaf" in blast_reports["blast_radius_summary"]
