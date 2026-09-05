"""Unit and integration tests for AntiOS 2.0 Context Budget Governor (Phase 87)."""

import unittest

from framework.core.context_budget import (
    ContextBudgetCard,
    ContextBudgetGovernor,
    ContextBudgetResult,
    ContextClassification,
    ContextSelectionDecision,
    ContextSourceItem,
    ContextSourceType,
    GovernorAction,
)


class TestContextBudgetGovernor(unittest.TestCase):
    """Test suite verifying deterministic context budgeting behavior."""

    def setUp(self):
        self.governor = ContextBudgetGovernor(token_budget=1000)

    def test_mandatory_safety_context_always_loaded(self):
        """Rule 1: Safety invariants and constitutional policies are unconditionally loaded."""
        safety_item = ContextSourceItem.create(
            source_id="core-guard",
            source_type=ContextSourceType.CONSTITUTIONAL_POLICY,
            title="Pre-Tool Guard Boundaries",
            content="Immutable zones: framework/, .agents/hooks.json, antios.config.json. Never bypass.",
            is_safety_critical=True,
            provenance="AntiOS Constitution",
        )
        sources = [safety_item]
        res = self.governor.evaluate(task_intent="Fix bug in calculation", sources=sources)

        self.assertEqual(len(res.decisions), 1)
        dec = res.decisions[0]
        self.assertEqual(dec.classification, ContextClassification.MANDATORY)
        self.assertEqual(dec.action, GovernorAction.LOAD)
        self.assertIn("Pre-Tool Guard Boundaries", res.loaded_context)

    def test_irrelevant_context_deferred(self):
        """Rule 2: Unrelated peripheral context is deferred rather than polluting prompt."""
        unrelated_item = ContextSourceItem.create(
            source_id="mobile-flutter-guide",
            source_type=ContextSourceType.PROJECT_SKILL,
            title="Flutter Mobile Widget Architecture Guide",
            content="Guidelines for rendering Flutter mobile widgets on iOS and Android devices.",
            is_safety_critical=False,
            provenance="docs/guides/flutter.md",
            target_files=["apps/mobile/lib/main.dart"],
        )
        sources = [unrelated_item]
        res = self.governor.evaluate(
            task_intent="Fix backend SQL migration query",
            sources=sources,
            active_files=["backend/migrations/001.sql"],
        )

        dec = res.decisions[0]
        self.assertEqual(dec.classification, ContextClassification.OPTIONAL)
        self.assertEqual(dec.action, GovernorAction.DEFER)
        self.assertNotIn("Flutter Mobile Widget", res.loaded_context)

    def test_redundant_context_deduplicated(self):
        """Rule 3: Duplicate observations or duplicate content are marked REDUNDANT and DISCARDED."""
        item1 = ContextSourceItem.create(
            source_id="obs-1",
            source_type=ContextSourceType.VALIDATED_KNOWLEDGE,
            title="Test Runner Observation",
            content="Use pytest to run test suite across workspace.",
        )
        item2 = ContextSourceItem.create(
            source_id="obs-2",
            source_type=ContextSourceType.VALIDATED_KNOWLEDGE,
            title="Duplicate Test Runner Observation",
            content="Use pytest to run test suite across workspace.",
        )
        sources = [item1, item2]
        res = self.governor.evaluate(task_intent="Run tests", sources=sources)

        dec1 = [d for d in res.decisions if d.source_id == "obs-1"][0]
        dec2 = [d for d in res.decisions if d.source_id == "obs-2"][0]

        self.assertEqual(dec1.action, GovernorAction.LOAD)
        self.assertEqual(dec2.classification, ContextClassification.REDUNDANT)
        self.assertEqual(dec2.action, GovernorAction.DISCARD)

    def test_stale_context_detected_and_refresh_mandated(self):
        """Rule 4: Stale context triggers REFRESH action and is excluded from active injection."""
        stale_item = ContextSourceItem.create(
            source_id="stale-manifest",
            source_type=ContextSourceType.PROJECT_ANATOMY,
            title="Outdated Project Manifest",
            content="Dependencies: flask==1.0",
            is_stale=True,
        )
        sources = [stale_item]
        res = self.governor.evaluate(task_intent="Install dependencies", sources=sources)

        dec = res.decisions[0]
        self.assertEqual(dec.classification, ContextClassification.STALE)
        self.assertEqual(dec.action, GovernorAction.REFRESH)
        self.assertIn("stale-manifest", res.card.refreshes_required)
        self.assertNotIn("flask==1.0", res.loaded_context)

    def test_useful_information_vs_context_cost_optimization(self):
        """Rule 5: Relevant sources prioritized by utility over raw token count."""
        high_utility_item = ContextSourceItem.create(
            source_id="target-module-api",
            source_type=ContextSourceType.COMPONENT_INTELLIGENCE,
            title="Target Adapter Class Specification",
            content="class DatabaseAdapter: def connect(self): ...",
            epistemic_weight=1.0,
            target_files=["backend/adapter.py"],
        )
        low_utility_large_item = ContextSourceItem.create(
            source_id="historical-release-notes",
            source_type=ContextSourceType.VALIDATED_KNOWLEDGE,
            title="Historical Release Notes v0.1",
            content="Release notes for version 0.1 from 2 years ago. " * 30,
            epistemic_weight=0.3,
            target_files=[],
        )
        # Small budget that can only fit one
        small_gov = ContextBudgetGovernor(token_budget=150)
        res = small_gov.evaluate(
            task_intent="Refactor DatabaseAdapter in adapter.py",
            sources=[low_utility_large_item, high_utility_item],
            active_files=["backend/adapter.py"],
        )

        loaded_ids = [d.source_id for d in res.decisions if d.action in (GovernorAction.LOAD, GovernorAction.SUMMARIZE)]
        self.assertIn("target-module-api", loaded_ids)
        self.assertNotIn("historical-release-notes", loaded_ids)

    def test_reasoning_card_strictly_bounded(self):
        """Rule 6: The reasoning card is strictly token-bounded (<= 16 lines)."""
        sources = [
            ContextSourceItem.create(
                source_id=f"item-{i}",
                source_type=ContextSourceType.VALIDATED_KNOWLEDGE,
                title=f"Source Item {i}",
                content=f"Content for item {i}",
            )
            for i in range(10)
        ]
        res = self.governor.evaluate(task_intent="General task", sources=sources)
        card_str = res.card.format_card()
        lines = card_str.splitlines()

        self.assertLessEqual(len(lines), 16)
        self.assertIn("ANTIOS CONTEXT BUDGET CARD", card_str)
        self.assertIn("Budget Ceiling:", card_str)


if __name__ == "__main__":
    unittest.main()
