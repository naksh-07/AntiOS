"""Unit tests for AntiOS Phase 28-30 Change-Intent Intelligence."""

import os
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import (
    KnowledgeGraph,
    ChangeIntentAnalyzer,
    ChangeIntent,
)
from framework.core.wayfinding import WayfindingEngine


def _build_test_engine():
    engine = WayfindingEngine(workspace_root="/test_repo")

    auth_decl = SubsystemDeclaration(
        subsystem_id="auth",
        name="Authentication Subsystem",
        description="Handles user identity and session persistence.",
        area="core",
        root_paths=["src/auth"],
        entrypoints=["src/auth/service.py"],
        authoritative_files=["src/auth/service.py"],
        covering_tests=["tests/test_auth.py"],
        test_commands=["pytest tests/test_auth.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Never log secret keys"],
        protected_invariants=["src/auth/crypto.py"],
        dependencies=[],
        consumers=["billing", "gateway"],
        documentation_paths=["docs/subsystems/auth.md"],
        keywords=["auth", "login"],
        purpose="User identity management",
        risk_tier="HIGH",
        owner="@security-team",
    )

    billing_decl = SubsystemDeclaration(
        subsystem_id="billing",
        name="Billing Subsystem",
        description="Processes invoices and payments.",
        area="finance",
        root_paths=["src/billing"],
        entrypoints=["src/billing/service.py"],
        authoritative_files=["src/billing/service.py"],
        covering_tests=["tests/test_billing.py"],
        test_commands=["pytest tests/test_billing.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=["Idempotent payment calls"],
        protected_invariants=[],
        dependencies=["auth"],
        consumers=["reports"],
        documentation_paths=[],
        keywords=["billing"],
        purpose="Payment processing",
        risk_tier="MEDIUM",
        owner="@finance-team",
    )

    reports_decl = SubsystemDeclaration(
        subsystem_id="reports",
        name="Reports Subsystem",
        description="Financial summaries.",
        area="analytics",
        root_paths=["src/reports"],
        entrypoints=["src/reports/main.py"],
        authoritative_files=["src/reports/main.py"],
        covering_tests=["tests/test_reports.py"],
        test_commands=["pytest tests/test_reports.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=[],
        protected_invariants=[],
        dependencies=["billing"],
        consumers=[],
        documentation_paths=[],
        keywords=["reports"],
        purpose="Analytics metrics",
        risk_tier="LOW",
        owner=None,
    )

    engine.register_subsystem(auth_decl)
    engine.register_subsystem(billing_decl)
    engine.register_subsystem(reports_decl)
    return engine


def test_change_intent_single_file_resolution():
    engine = _build_test_engine()
    intent = engine.analyze_change(["src/auth/service.py"])

    assert intent.target_files == ["src/auth/service.py"]
    assert "auth" in intent.affected_subsystems
    assert intent.risk_tier == "HIGH"
    assert "billing" in intent.transitive_consumers
    assert "reports" in intent.transitive_consumers
    assert "pytest tests/test_auth.py" in intent.test_commands
    assert "src/auth/crypto.py" in intent.protected_invariants_at_risk
    assert "@security-team" in intent.owners


def test_change_intent_leaf_component_low_risk():
    engine = _build_test_engine()
    intent = engine.analyze_change(["src/reports/main.py"])

    assert intent.affected_subsystems == ["reports"]
    assert intent.risk_tier == "LOW"
    assert intent.transitive_consumers == []
    assert "pytest tests/test_reports.py" in intent.test_commands


def test_change_intent_multi_subsystem_change():
    engine = _build_test_engine()
    intent = engine.analyze_change(["src/auth/service.py", "src/billing/service.py"])

    assert "auth" in intent.affected_subsystems
    assert "billing" in intent.affected_subsystems
    assert intent.risk_tier == "HIGH"
    assert "pytest tests/test_auth.py" in intent.test_commands
    assert "pytest tests/test_billing.py" in intent.test_commands
    assert any("Maker-Checker" in v for v in intent.required_verification)


def test_change_intent_unmapped_unknown_file():
    engine = _build_test_engine()
    intent = engine.analyze_change(["scripts/deploy_untracked.sh"])

    assert intent.affected_subsystems == ["UNKNOWN"]
    assert "outside registered subsystems" in intent.blast_radius_summary
    assert "Project root test runner" in intent.required_verification


def test_change_intent_empty_target_files():
    engine = _build_test_engine()
    intent = engine.analyze_change([])

    assert intent.affected_subsystems == []
    assert intent.risk_tier == "LOW"
    assert "Empty change set" in intent.blast_radius_summary


def test_change_intent_card_formatting_bounded():
    engine = _build_test_engine()
    intent = engine.analyze_change(["src/auth/service.py"])
    card = engine.change_analyzer.format_change_intent_card(intent)

    assert "=== ANTIOS CHANGE INTENT CARD ===" in card
    assert "Target:       src/auth/service.py" in card
    assert "Subsystem:    auth [Risk: HIGH]" in card
    assert "Runners:      pytest tests/test_auth.py" in card

    lines = card.strip().splitlines()
    assert len(lines) <= 25, f"Card exceeds 25 lines: {len(lines)}"
