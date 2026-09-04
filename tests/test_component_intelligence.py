"""Tests for AntiOS 2.0 Phase 56: Component Intelligence.

Verifies:
- Pre-modification intelligence resolution answering "what do I need to know before modifying it?"
- Authoritative files, entrypoints, interfaces, dependencies, and consumers.
- Downstream blast radius and covering test suites.
- Token-bounded card rendering (<= 25 lines).
- Integration into WayfindingEngine.
"""

import os
from pathlib import Path
import unittest

from framework.core.component_intelligence import (
    ComponentIntelligenceReport,
    ComponentIntelligenceResolver,
)
from framework.core.knowledge import KnowledgeGraph
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


class TestComponentIntelligence(unittest.TestCase):
    """Unit tests for ComponentIntelligenceResolver and reports."""

    def setUp(self):
        self.wayfinding = WayfindingEngine(workspace_root=str(Path(__file__).parent.parent))

        # Register a UI component subsystem
        self.ui_sub = SubsystemDeclaration.from_dict({
            "subsystem_id": "auth_ui",
            "name": "Authentication UI",
            "area": "ui",
            "description": "Login, signup, and password reset views with buttons and inputs",
            "root_paths": ["src/components/auth"],
            "entrypoints": ["src/components/auth/LoginButton.tsx", "src/components/auth/LoginForm.tsx"],
            "authoritative_files": ["src/components/auth/LoginButton.tsx"],
            "covering_tests": ["tests/LoginButton.test.tsx"],
            "test_commands": ["npm test tests/LoginButton.test.tsx"],
            "applicable_skills": ["frontend-design", "antios-engineer"],
            "applicable_workflows": [],
            "governing_rules": ["rule:design-system-tokens", "rule:a11y-wcag-aa"],
            "protected_invariants": ["invariant:oauth-callback-url"],
            "dependencies": ["auth_api"],
            "consumers": ["app_router"],
            "documentation_paths": ["docs/subsystems/auth.md"],
            "keywords": ["login", "button", "auth", "signin", "signup"],
            "risk_tier": "HIGH",
            "owner": "Frontend Core Team",
            "owner_source": "CODEOWNERS",
            "owner_confidence": 1.0,
            "purpose": "Renders user authentication interface controls",
        })
        self.wayfinding.register_subsystem(self.ui_sub)

    def test_resolve_component_intelligence_from_intent(self):
        # Query: "Change the login button"
        report = self.wayfinding.get_component_intelligence("Change the login button")
        self.assertIsNotNone(report)
        self.assertIsInstance(report, ComponentIntelligenceReport)
        self.assertEqual(report.component_id, "auth_ui")
        self.assertEqual(report.identity, "Authentication UI")
        self.assertIn("src/components/auth/LoginButton.tsx", report.authoritative_location)
        self.assertIn("auth_api", report.dependencies)
        self.assertIn("app_router", report.consumers)
        self.assertIn("tests/LoginButton.test.tsx", report.covering_tests)
        self.assertIn("npm test tests/LoginButton.test.tsx", report.test_commands)
        self.assertEqual(report.owner, "Frontend Core Team")
        self.assertEqual(report.risk_tier, "HIGH")

        # High risk requires Maker-Checker ratchet
        self.assertTrue(any("Maker-Checker" in r for r in report.verification_requirements))

    def test_render_component_intelligence_card_bounded(self):
        card = self.wayfinding.render_component_intelligence_card("login button")
        self.assertIsInstance(card, str)
        self.assertIn("Component Intelligence", card)
        self.assertIn("Authentication UI", card)
        lines = card.splitlines()
        # Strictly bounded <= 25 lines
        self.assertLessEqual(len(lines), 25)

    def test_unknown_query_returns_none(self):
        report = self.wayfinding.get_component_intelligence("completely unknown query xyz123")
        self.assertIsNone(report)
        card = self.wayfinding.render_component_intelligence_card("completely unknown query xyz123")
        self.assertIn("No component matched", card)


if __name__ == "__main__":
    unittest.main()
