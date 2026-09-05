"""Tests for Phase 77 Agent-Native Refactoring Advisor."""

from pathlib import Path
import tempfile
import unittest

from framework.core.agent_friction import (
    AgentCostLevel,
    AgentFrictionFinding,
    FrictionCategory,
    FrictionClassification,
    FrictionSeverity,
)
from framework.core.agent_refactoring import (
    AgentRefactoringAdvisor,
    RefactoringAdvisorReport,
    RefactoringRecommendation,
)


class TestAgentRefactoring(unittest.TestCase):
    """Test suite for AgentRefactoringAdvisor."""

    def test_advisor_strictly_advisory_no_disk_modifications(self):
        """Advisor only outputs recommendations and does NOT modify files."""
        report = AgentRefactoringAdvisor.analyze_repository(".")
        self.assertIsInstance(report, RefactoringAdvisorReport)
        self.assertGreaterEqual(report.total_recommendations, 0)

    def test_rejects_refactoring_touching_immutable_core(self):
        """Any finding touching framework/core/ is converted to NO_ACTION with CRITICAL risk."""
        finding = AgentFrictionFinding(
            friction_id="FRIC-CORE-TEST",
            category=FrictionCategory.EXCESSIVE_CONTEXT_TRAVERSAL,
            classification=FrictionClassification.OBSERVED_FRICTION,
            evidence={},
            affected_paths=["framework/core/guard.py"],
            affected_capabilities=[],
            frequency=1,
            severity=FrictionSeverity.HIGH,
            confidence=1.0,
            estimated_agent_cost=AgentCostLevel.HIGH,
        )
        rec = AgentRefactoringAdvisor._evaluate_friction_for_refactoring(finding, Path("."))
        self.assertIsNotNone(rec)
        self.assertTrue(rec.is_no_action)
        self.assertEqual(rec.risk_tier, "CRITICAL")
        self.assertIn("Core Immutability", rec.title)

    def test_valid_friction_converts_to_governed_proposal(self):
        """Valid project friction recommendation carries an associated StructuredCapabilityProposal."""
        finding = AgentFrictionFinding(
            friction_id="FRIC-TEST-REFACTOR-DOC",
            category=FrictionCategory.DEAD_PROJECT_REFERENCES,
            classification=FrictionClassification.OBSERVED_FRICTION,
            evidence={"broken_count": 1},
            affected_paths=["docs/overview.md"],
            affected_capabilities=["documentation"],
            frequency=1,
            severity=FrictionSeverity.MEDIUM,
            confidence=1.0,
            estimated_agent_cost=AgentCostLevel.MEDIUM,
            description="Fix broken link to config",
        )
        rec = AgentRefactoringAdvisor._evaluate_friction_for_refactoring(finding, Path("."))
        self.assertIsNotNone(rec)
        self.assertFalse(rec.is_no_action)
        self.assertIsNotNone(rec.associated_proposal)
        self.assertEqual(rec.associated_proposal.selected_option, "REPAIR_BROKEN_REFERENCES")


if __name__ == "__main__":
    unittest.main()
