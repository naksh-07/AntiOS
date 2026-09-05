"""Tests for Phase 75 Improvement Proposal Engine."""

import unittest

from framework.core.agent_friction import (
    AgentCostLevel,
    AgentFrictionFinding,
    FrictionCategory,
    FrictionClassification,
    FrictionSeverity,
)
from framework.core.agent_improvement import ImprovementProposalEngine
from framework.core.evolution_governance import ApprovalClass, ControlledEvolutionGovernor
from framework.core.evolution_proposal import (
    ProposalApprovalState,
    StructuredCapabilityProposal,
    StructuredProposalType,
)


class TestAgentImprovement(unittest.TestCase):
    """Test suite for ImprovementProposalEngine."""

    def test_no_action_for_weak_evidence(self):
        """Low confidence (< 0.6) friction triggers explicit NO_ACTION."""
        f = AgentFrictionFinding(
            friction_id="FRIC-TEST-LOWCONF",
            category=FrictionCategory.REPEATED_SEARCH,
            classification=FrictionClassification.POSSIBLE_FRICTION,
            evidence={},
            affected_paths=["src/"],
            affected_capabilities=[],
            frequency=1,
            severity=FrictionSeverity.LOW,
            confidence=0.4,
            estimated_agent_cost=AgentCostLevel.LOW,
        )
        prop = ImprovementProposalEngine.propose_from_friction(f)
        self.assertEqual(prop.proposal_type, StructuredProposalType.NO_ACTION)
        self.assertEqual(prop.selected_option, "NO_ACTION")

    def test_propose_dead_reference_repair(self):
        """Dead project reference friction produces DOCUMENTATION_IMPROVEMENT proposal."""
        f = AgentFrictionFinding(
            friction_id="FRIC-TEST-DEADREF",
            category=FrictionCategory.DEAD_PROJECT_REFERENCES,
            classification=FrictionClassification.OBSERVED_FRICTION,
            evidence={"broken_count": 2},
            affected_paths=["docs/guide.md"],
            affected_capabilities=["documentation"],
            frequency=2,
            severity=FrictionSeverity.HIGH,
            confidence=1.0,
            estimated_agent_cost=AgentCostLevel.MEDIUM,
        )
        prop = ImprovementProposalEngine.propose_from_friction(f)
        self.assertEqual(prop.proposal_type, StructuredProposalType.DOCUMENTATION_IMPROVEMENT)
        self.assertTrue(len(prop.verification_plan) > 0)
        self.assertTrue(len(prop.rollback_plan) > 0)
        self.assertEqual(prop.approval_state, ProposalApprovalState.PROPOSED)

    def test_propose_mcp_reduction(self):
        """MCP escalation produces MCP_ESCALATION_REDUCTION proposal."""
        f = AgentFrictionFinding(
            friction_id="FRIC-TEST-MCP",
            category=FrictionCategory.UNNECESSARY_MCP_ESCALATION,
            classification=FrictionClassification.INFERRED_FRICTION,
            evidence={"mcp": "github"},
            affected_paths=["antios.config.json"],
            affected_capabilities=["tool_policy"],
            frequency=1,
            severity=FrictionSeverity.MEDIUM,
            confidence=0.9,
            estimated_agent_cost=AgentCostLevel.HIGH,
        )
        prop = ImprovementProposalEngine.propose_from_friction(f)
        self.assertEqual(prop.proposal_type, StructuredProposalType.MCP_ESCALATION_REDUCTION)
        self.assertEqual(prop.selected_option, "ENFORCE_TIER_4_CLI")

    def test_proposal_governance_compatibility(self):
        """Generated proposals are directly evaluatable by ControlledEvolutionGovernor."""
        f = AgentFrictionFinding(
            friction_id="FRIC-TEST-GOV",
            category=FrictionCategory.AMBIGUOUS_OWNERSHIP,
            classification=FrictionClassification.OBSERVED_FRICTION,
            evidence={},
            affected_paths=[".antios/manifest.json"],
            affected_capabilities=["ownership"],
            frequency=1,
            severity=FrictionSeverity.HIGH,
            confidence=1.0,
            estimated_agent_cost=AgentCostLevel.HIGH,
        )
        prop = ImprovementProposalEngine.propose_from_friction(f)
        approval_class, reason = ControlledEvolutionGovernor.classify_proposal_approval(prop)
        self.assertIn(approval_class, [ApprovalClass.AUTO_EXECUTABLE, ApprovalClass.GOVERNANCE_REQUIRED])


if __name__ == "__main__":
    unittest.main()
