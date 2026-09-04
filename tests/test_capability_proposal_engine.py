"""Tests for AntiOS 2.0 Phase 70: Capability Proposal Engine."""

from __future__ import annotations
import unittest

from framework.core.capability_gap import CapabilityGap, CapabilityGapDetector, GapClassification, GapStatus
from framework.core.evolution_proposal import (
    AlternativeOption,
    CapabilityProposalEngine,
    ProposalApprovalState,
    StructuredCapabilityProposal,
    StructuredProposalType,
)


class TestCapabilityProposalEngine(unittest.TestCase):
    """Unit tests for the Capability Proposal Engine."""

    def test_proposal_roundtrip_serialization(self):
        """Test serializing StructuredCapabilityProposal to dict and restoring."""
        alt1 = AlternativeOption(
            option_name="Option A",
            description="Do A",
            estimated_cost="ZERO",
            risk_level="LOW",
            why_selected_or_rejected="Selected",
            is_selected=True,
        )
        alt2 = AlternativeOption(
            option_name="Option B",
            description="Do B",
            estimated_cost="MEDIUM",
            risk_level="HIGH",
            why_selected_or_rejected="Rejected",
            is_selected=False,
        )
        prop = StructuredCapabilityProposal(
            proposal_id="prop-test-001",
            gap_id="gap-comp-12345678",
            proposal_type=StructuredProposalType.ADD_PROJECT_SKILL,
            evidence={"exit_code": 1},
            rationale="Need a project skill",
            alternatives=[alt1, alt2],
            selected_option="Option A",
            risk_tier="LOW",
            blast_radius=["compiler"],
            affected_paths=[".agents/skills/test-skill/SKILL.md"],
            required_tools=["write_to_file"],
            required_skills=["antios-engineer"],
            required_agents=["AntiOS Engineer"],
            verification_plan=["python tests/run_all.py"],
            rollback_plan=["git restore ."],
            approval_state=ProposalApprovalState.PROPOSED,
            confidence=0.9,
        )
        d = prop.to_dict()
        self.assertEqual(d["proposal_id"], "prop-test-001")
        self.assertEqual(d["proposal_type"], "ADD_PROJECT_SKILL")
        self.assertEqual(len(d["alternatives"]), 2)

        restored = StructuredCapabilityProposal.from_dict(d)
        self.assertEqual(restored.proposal_id, prop.proposal_id)
        self.assertEqual(restored.proposal_type, prop.proposal_type)
        self.assertEqual(len(restored.alternatives), 2)
        self.assertEqual(restored.alternatives[0].option_name, "Option A")
        self.assertTrue(restored.alternatives[0].is_selected)

    def test_no_action_for_ordinary_implementation_failure(self):
        """Ordinary implementation failure generates an explicit NO_ACTION proposal."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="fix syntax bug",
            subsystem="compiler",
            required_capability="python_code",
            current_capabilities=["python_runtime"],
            failure_evidence={"error": "SyntaxError: invalid syntax"},
            classification=GapClassification.ORDINARY_IMPLEMENTATION_FAILURE,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.NO_ACTION)
        self.assertEqual(prop.selected_option, "NO_ACTION")
        self.assertEqual(len(prop.affected_paths), 0)
        self.assertIn("resolve via standard debugging", prop.rationale)

    def test_no_action_for_verification_failure(self):
        """Verification failure (failing test) generates NO_ACTION."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="run unit tests",
            subsystem="core",
            required_capability="test_runner",
            current_capabilities=["unittest"],
            failure_evidence={"exit_code": 1},
            classification=GapClassification.VERIFICATION_FAILURE,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.NO_ACTION)
        self.assertEqual(prop.selected_option, "NO_ACTION")

    def test_no_action_for_insufficient_evidence(self):
        """Insufficient evidence generates NO_ACTION."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="deploy to production",
            subsystem="ops",
            required_capability="cloud_deployer",
            current_capabilities=[],
            failure_evidence={"unsubstantiated": True},
            classification=GapClassification.INSUFFICIENT_EVIDENCE,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.NO_ACTION)

    def test_propose_add_tool_adapter_for_missing_tool(self):
        """Missing tool runner in config generates ADD_TOOL_ADAPTER targeting antios.config.json."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="run gradle build",
            subsystem="build",
            required_capability="gradle",
            current_capabilities=[],
            failure_evidence={"missing_tool": "gradle"},
            classification=GapClassification.UNAVAILABLE_TOOL,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.ADD_TOOL_ADAPTER)
        self.assertIn("antios.config.json", prop.affected_paths)
        self.assertTrue(any("Register Tool" in a.option_name for a in prop.alternatives if a.is_selected))

    def test_propose_add_specialist_enforces_shallow_depth(self):
        """Specialist synthesis proposal must enforce max_depth<=2 and can_delegate=False."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="optimize database queries",
            subsystem="database",
            required_capability="specialist:db_optimizer",
            current_capabilities=["AntiOS Engineer"],
            failure_evidence={"slow_query_count": 50},
            classification=GapClassification.MISSING_CAPABILITY,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.ADD_SPECIALIST)
        self.assertIn(".antios/agent_topology.json", prop.affected_paths)
        self.assertEqual(prop.metadata.get("max_depth"), 2)
        self.assertFalse(prop.metadata.get("can_delegate"))

    def test_propose_add_project_skill(self):
        """Missing workflow capability proposes adding a project-local skill."""
        gap = CapabilityGapDetector.create_gap(
            task_intent="package helm chart",
            subsystem="kubernetes",
            required_capability="helm_packager",
            current_capabilities=[],
            failure_evidence={"cmd": "helm package"},
            classification=GapClassification.MISSING_CAPABILITY,
        )
        prop = CapabilityProposalEngine.evaluate_and_propose(gap)
        self.assertEqual(prop.proposal_type, StructuredProposalType.ADD_PROJECT_SKILL)
        self.assertTrue(any(".agents/skills/skill-kubernetes/SKILL.md" in p for p in prop.affected_paths))
        self.assertTrue(len(prop.verification_plan) > 0)
        self.assertTrue(len(prop.rollback_plan) > 0)


if __name__ == "__main__":
    unittest.main()
