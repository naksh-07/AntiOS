"""Unit tests for AntiOS Phase 28-30 Knowledge-Integrated Wayfinding."""

import os
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import ProgressiveDisclosureLevel
from framework.core.wayfinding import WayfindingEngine


def _build_test_engine():
    engine = WayfindingEngine(workspace_root="/mock_repo")
    auth_decl = SubsystemDeclaration(
        subsystem_id="auth",
        name="Authentication Subsystem",
        description="Handles user identity and session persistence.",
        area="security",
        root_paths=["src/auth"],
        entrypoints=["src/auth/service.py"],
        authoritative_files=["src/auth/service.py"],
        covering_tests=["tests/test_auth.py"],
        test_commands=["pytest tests/test_auth.py"],
        applicable_skills=["antios-engineer", "antios-debug"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Token expiration check required"],
        protected_invariants=["src/auth/crypto.py"],
        dependencies=["db"],
        consumers=["billing", "gateway"],
        documentation_paths=["docs/subsystems/auth.md"],
        keywords=["auth", "login"],
        purpose="User identity management",
        risk_tier="HIGH",
        owner="@security-team",
    )
    engine.register_subsystem(auth_decl)
    return engine


def test_wayfinding_resolve_component_direct():
    engine = _build_test_engine()
    res = engine.resolve_component("auth")
    assert res is not None
    assert res.matched_subsystem_id == "auth"
    assert res.risk_tier == "HIGH"
    assert res.owner == "@security-team"


def test_wayfinding_get_capabilities():
    engine = _build_test_engine()
    caps = engine.get_capabilities("auth")
    assert caps["subsystem_id"] == "auth"
    assert "antios-engineer" in caps["skills"]
    assert "antios-debug" in caps["skills"]
    assert "FEATURE" in caps["workflows"]
    assert "BUG" in caps["workflows"]
    assert any("Token expiration" in r for r in caps["rules"])


def test_wayfinding_get_blast_radius():
    engine = _build_test_engine()
    blast = engine.get_blast_radius("auth")
    assert blast["component_id"] == "auth"
    assert "billing" in blast["direct_consumers"]
    assert "gateway" in blast["direct_consumers"]


def test_wayfinding_locate_progressive():
    engine = _build_test_engine()
    res, card = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L1)
    assert res is not None
    assert "=== ANTIOS L1 LOCATOR ===" in card
    assert "Subsystem:   auth" in card

    res2, card2 = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L2)
    assert "=== ANTIOS L2 COMPONENT KNOWLEDGE ===" in card2
    assert "Risk: HIGH" in card2
