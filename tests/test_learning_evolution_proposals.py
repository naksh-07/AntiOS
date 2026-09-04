"""Tests for AntiOS 2.0 Phase 64: Safe Skill & Knowledge Evolution Proposals."""

from __future__ import annotations
import tempfile
from pathlib import Path
import unittest

from framework.core.learning import (
    CandidateLesson,
    EvolutionProposal,
    EvolutionProposalEngine,
    LearningSafetyGate,
    ProposalType,
)
from framework.core.memory import KnowledgeAuthority


class TestLearningEvolutionProposals(unittest.TestCase):
    """Test suite verifying safe proposal generation without silent file mutation."""

    def test_validated_lesson_generates_structured_proposal(self):
        """Verify validated lesson generates an explicit proposal with audit trails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lesson = CandidateLesson(
                lesson_id="les-validated-1",
                title="Frontend icons require SVG sanitization before render",
                trigger_or_failure="SVG XSS risk in icon loader",
                rule_or_action="Sanitize SVG using DOMPurify before mounting",
                authority=KnowledgeAuthority.VALIDATED,
                evidence_observation_ids=["obs-xss-1", "obs-fix-1"],
                task_ids=["task-1", "task-2"],
                recurrence_count=2,
                category="frontend-skill",
                affected_subsystem="frontend",
                confidence=0.85,
            )

            proposal = EvolutionProposalEngine.generate_proposal(lesson, tmpdir)
            self.assertIsNotNone(proposal)
            self.assertIsInstance(proposal, EvolutionProposal)
            self.assertEqual(proposal.proposal_type, ProposalType.SKILL_UPDATE)
            self.assertEqual(proposal.status, "PENDING_REVIEW")
            self.assertTrue(proposal.requires_human_approval)
            self.assertIn("Sanitize SVG", proposal.what_should_change)
            self.assertIn("frontend", proposal.blast_radius)
            self.assertEqual(proposal.lesson_id, "les-validated-1")
            self.assertEqual(proposal.evidence_observation_ids, ["obs-xss-1", "obs-fix-1"])

    def test_unvalidated_candidate_cannot_generate_proposal(self):
        """Verify unvalidated candidate lesson cannot emit evolution proposals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lesson = CandidateLesson(
                lesson_id="les-cand-raw",
                title="Provisional hypothesis",
                trigger_or_failure="Single unverified error",
                rule_or_action="Tentative change",
                authority=KnowledgeAuthority.CANDIDATE,
                confidence=0.4,
            )

            proposal = EvolutionProposalEngine.generate_proposal(lesson, tmpdir)
            self.assertIsNone(proposal)

    def test_core_boundary_immutable_denies_core_mutation_proposals(self):
        """CRITICAL: Proposal attempting to mutate AntiOS Core or Constitution must be blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            illegal_proposal = EvolutionProposal(
                proposal_id="prop-illegal-core",
                proposal_type=ProposalType.DOCUMENTATION_UPDATE,
                target_artifact="ANTIOS_CONSTITUTION.md",
                what_should_change="Relax four boundary demarcation rule",
                why="Agent wants broader permissions",
                requires_human_approval=True,
            )

            is_safe, reason = LearningSafetyGate.validate_proposal(illegal_proposal, tmpdir)
            self.assertFalse(is_safe)
            self.assertIn("strictly prohibited from mutating AntiOS Core", reason)

            # Also check framework/core path
            illegal_framework_prop = EvolutionProposal(
                proposal_id="prop-illegal-fw",
                proposal_type=ProposalType.SKILL_UPDATE,
                target_artifact="framework/core/guard.py",
                what_should_change="Bypass stop gate check",
                why="Speed up execution",
                requires_human_approval=True,
            )

            is_safe2, reason2 = LearningSafetyGate.validate_proposal(illegal_framework_prop, tmpdir)
            self.assertFalse(is_safe2)
            self.assertIn("strictly prohibited from mutating AntiOS Core", reason2)

    def test_specialist_self_promotion_strictly_blocked(self):
        """Verify proposals granting delegation authority to specialists are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self_promo_prop = EvolutionProposal(
                proposal_id="prop-self-promo",
                proposal_type=ProposalType.SPECIALIST_CAPABILITY,
                target_artifact=".antios/agent_topology.json",
                what_should_change="Set can_delegate=True and increase max_depth to 4",
                why="Specialist needs to spawn child subagents",
                requires_human_approval=True,
            )

            is_safe, reason = LearningSafetyGate.validate_proposal(self_promo_prop, tmpdir)
            self.assertFalse(is_safe)
            self.assertIn("Shallow Depth Law Violation", reason)

    def test_mcp_authority_escalation_strictly_blocked(self):
        """Verify proposals attempting to escalate MCP tool permissions are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mcp_escalation_prop = EvolutionProposal(
                proposal_id="prop-mcp-escalate",
                proposal_type=ProposalType.PROJECT_CONVENTION,
                target_artifact="antios.config.json",
                what_should_change="Enable mcp root execute and grant all docker permissions",
                why="Allow broad automated execution",
                requires_human_approval=True,
            )

            is_safe, reason = LearningSafetyGate.validate_proposal(mcp_escalation_prop, tmpdir)
            self.assertFalse(is_safe)
            self.assertIn("Authority Escalation Violation", reason)

    def test_silent_mutation_applied_without_human_approval_blocked(self):
        """Verify that a proposal marked APPLIED without human approval is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            silent_prop = EvolutionProposal(
                proposal_id="prop-silent",
                proposal_type=ProposalType.PROJECT_CONVENTION,
                target_artifact="antios.config.json",
                what_should_change="Auto-apply new convention",
                why="Autonomous evolution",
                requires_human_approval=True,
                status="APPLIED",
            )

            is_safe, reason = LearningSafetyGate.validate_proposal(silent_prop, tmpdir)
            self.assertFalse(is_safe)
            self.assertIn("require explicit human approval", reason)


if __name__ == "__main__":
    unittest.main()
