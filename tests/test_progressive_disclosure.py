"""Unit tests for AntiOS Phase 28-30 Progressive Disclosure Engine."""

import json
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import (
    ProgressiveDisclosureLevel,
    ProgressiveDisclosureEngine,
    KnowledgeGraph,
)
from framework.core.wayfinding import WayfindingEngine


def _build_test_resolution():
    engine = WayfindingEngine(workspace_root="/mock_repo")
    decl = SubsystemDeclaration(
        subsystem_id="billing",
        name="Billing & Payments",
        description="Processes customer invoices, Stripe webhooks, and subscriptions.",
        area="finance",
        root_paths=["src/billing"],
        entrypoints=["src/billing/service.py", "src/billing/client.py"],
        authoritative_files=["src/billing/service.py", "src/billing/types.py"],
        covering_tests=["tests/test_billing.py"],
        test_commands=["pytest tests/test_billing.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Ensure charge idempotency"],
        protected_invariants=["src/billing/stripe_keys.py"],
        dependencies=["auth", "db"],
        consumers=["reports", "notifications"],
        documentation_paths=["docs/subsystems/billing.md"],
        keywords=["billing", "payment", "invoice"],
        purpose="Processes financial transactions and recurring billing",
        risk_tier="HIGH",
        owner="@finance-team",
        owner_source="CODEOWNERS",
        owner_confidence=0.95,
        epistemic_state="OBSERVED",
    )
    engine.register_subsystem(decl)
    return engine, engine.locate("billing")


def test_progressive_disclosure_level_0_project_identity():
    proj_info = {
        "name": "AntiOS-TestApp",
        "archetype": "monorepo",
        "total_subsystems": 5,
        "primary_tech": "Python / TypeScript",
    }
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L0_PROJECT_IDENTITY, proj_info)
    assert "[AntiOS L0 Project]" in card
    assert "Name: AntiOS-TestApp" in card
    assert "Subsystems: 5" in card
    lines = card.strip().splitlines()
    assert len(lines) <= 5, f"L0 card exceeds 5 lines: {len(lines)}"


def test_progressive_disclosure_level_1_subsystem_locator():
    engine, res = _build_test_resolution()
    assert res is not None
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L1_SUBSYSTEM_LOCATOR, res)

    assert "=== ANTIOS L1 LOCATOR ===" in card
    assert "Subsystem:   billing" in card
    assert "Entrypoints: src/billing/service.py" in card
    lines = card.strip().splitlines()
    assert len(lines) <= 15, f"L1 card exceeds 15 lines: {len(lines)}"


def test_progressive_disclosure_level_2_component_knowledge():
    engine, res = _build_test_resolution()
    assert res is not None
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L2_COMPONENT_KNOWLEDGE, res)

    assert "=== ANTIOS L2 COMPONENT KNOWLEDGE ===" in card
    assert "Component:    billing" in card
    assert "Key Files:    src/billing/service.py" in card
    assert "CoveringTests:tests/test_billing.py" in card
    lines = card.strip().splitlines()
    assert len(lines) <= 20, f"L2 card exceeds 20 lines: {len(lines)}"


def test_progressive_disclosure_level_3_relationships_and_blast_radius():
    engine, res = _build_test_resolution()
    assert res is not None
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L3_RELATIONSHIPS_AND_BLAST_RADIUS, res, engine.knowledge_graph)

    assert "=== ANTIOS L3 RELATIONSHIPS & BLAST RADIUS ===" in card
    assert "Depends On:   auth, db" in card
    assert "Consumed By:  notifications, reports" in card
    assert "downstream components affected" in card
    lines = card.strip().splitlines()
    assert len(lines) <= 25, f"L3 card exceeds 25 lines: {len(lines)}"


def test_progressive_disclosure_level_4_capabilities():
    engine, res = _build_test_resolution()
    assert res is not None
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L4_CAPABILITIES, res)

    assert "=== ANTIOS L4 CAPABILITIES & GOVERNANCE ===" in card
    assert "Skills:       antios-engineer" in card
    assert "Rules:        Ensure charge idempotency" in card
    lines = card.strip().splitlines()
    assert len(lines) <= 20, f"L4 card exceeds 20 lines: {len(lines)}"


def test_progressive_disclosure_level_5_detailed_evidence():
    engine, res = _build_test_resolution()
    assert res is not None
    card = ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L5_DETAILED_EVIDENCE, res)

    parsed = json.loads(card)
    assert parsed["matched_subsystem_id"] == "billing"
    assert parsed["risk_tier"] == "HIGH"
    assert parsed["owner"] == "@finance-team"
    assert parsed["owner_confidence"] == 0.95
    assert parsed["epistemic_state"] == "OBSERVED"
