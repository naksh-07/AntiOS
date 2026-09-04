"""Tests for AntiOS 2.0 Phase 71: Controlled AntiOS Evolution Governance."""

from __future__ import annotations
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.evolution_governance import (
    ApprovalClass,
    ControlledEvolutionGovernor,
    EvolutionExecutionResult,
    EvolutionSnapshot,
)
from framework.core.evolution_proposal import (
    AlternativeOption,
    ProposalApprovalState,
    StructuredCapabilityProposal,
    StructuredProposalType,
)
from framework.core.manifest import ProjectManifest, load_manifest, save_manifest


class TestControlledEvolutionGovernance(unittest.TestCase):
    """Unit tests for the Controlled AntiOS Evolution Governor."""

    def test_core_immutable_denied_classification(self):
        """Proposals targeting framework/core or constitution are strictly denied."""
        targets = [
            "framework/core/guard.py",
            "ANTIOS_CONSTITUTION.md",
            "antios_v1.md",
            ".agents/hooks.json",
            ".git/HEAD",
        ]
        for t in targets:
            prop = StructuredCapabilityProposal(
                proposal_id="prop-core-tamper",
                gap_id="gap-1",
                proposal_type=StructuredProposalType.UPDATE_TOOL_POLICY,
                evidence={},
                rationale="modify core",
                alternatives=[],
                selected_option="modify",
                risk_tier="LOW",
                blast_radius=["core"],
                affected_paths=[t],
                required_tools=[],
                required_skills=[],
                required_agents=[],
                verification_plan=[],
                rollback_plan=[],
            )
            app_class, reason = ControlledEvolutionGovernor.classify_proposal_approval(prop)
            self.assertEqual(app_class, ApprovalClass.CORE_IMMUTABLE_DENIED)
            self.assertIn("resides in immutable AntiOS core", reason)

    def test_specialist_self_promotion_denied(self):
        """Proposals attempting to give a specialist can_delegate=True are denied."""
        prop = StructuredCapabilityProposal(
            proposal_id="prop-spec-promo",
            gap_id="gap-2",
            proposal_type=StructuredProposalType.ADD_SPECIALIST,
            evidence={"can_delegate": True, "specialist": "lead"},
            rationale="allow specialist delegation",
            alternatives=[],
            selected_option="promo",
            risk_tier="HIGH",
            blast_radius=["agents"],
            affected_paths=[".antios/agent_topology.json"],
            required_tools=[],
            required_skills=[],
            required_agents=[],
            verification_plan=[],
            rollback_plan=[],
        )
        app_class, reason = ControlledEvolutionGovernor.classify_proposal_approval(prop)
        self.assertEqual(app_class, ApprovalClass.CORE_IMMUTABLE_DENIED)
        self.assertIn("Shallow Depth Law Violation", reason)

    def test_auto_executable_classification(self):
        """Low risk proposals targeting antios.config.json or generated topology are auto-executable."""
        prop = StructuredCapabilityProposal(
            proposal_id="prop-auto-cfg",
            gap_id="gap-3",
            proposal_type=StructuredProposalType.ADD_TOOL_ADAPTER,
            evidence={},
            rationale="add cargo test runner",
            alternatives=[],
            selected_option="add",
            risk_tier="LOW",
            blast_radius=["config"],
            affected_paths=["antios.config.json"],
            required_tools=[],
            required_skills=[],
            required_agents=[],
            verification_plan=[],
            rollback_plan=[],
        )
        app_class, _ = ControlledEvolutionGovernor.classify_proposal_approval(prop)
        self.assertEqual(app_class, ApprovalClass.AUTO_EXECUTABLE)

    def test_governance_required_classification(self):
        """Medium/High risk or skill additions require human governance sign-off."""
        prop = StructuredCapabilityProposal(
            proposal_id="prop-gov-skill",
            gap_id="gap-4",
            proposal_type=StructuredProposalType.ADD_PROJECT_SKILL,
            evidence={},
            rationale="create new project skill",
            alternatives=[],
            selected_option="create",
            risk_tier="MEDIUM",
            blast_radius=["skills"],
            affected_paths=[".agents/skills/my-skill/SKILL.md"],
            required_tools=[],
            required_skills=[],
            required_agents=[],
            verification_plan=[],
            rollback_plan=[],
        )
        app_class, reason = ControlledEvolutionGovernor.classify_proposal_approval(prop)
        self.assertEqual(app_class, ApprovalClass.GOVERNANCE_REQUIRED)
        self.assertIn("explicit human review required", reason)

    def test_apply_core_immutable_denied_fails_immediately(self):
        """Applying a CORE_IMMUTABLE_DENIED proposal fails without touching disk."""
        prop = StructuredCapabilityProposal(
            proposal_id="prop-fail-core",
            gap_id="gap-5",
            proposal_type=StructuredProposalType.UPDATE_TOOL_POLICY,
            evidence={},
            rationale="tamper core",
            alternatives=[],
            selected_option="",
            risk_tier="HIGH",
            blast_radius=["core"],
            affected_paths=["framework/core/security.py"],
            required_tools=[],
            required_skills=[],
            required_agents=[],
            verification_plan=[],
            rollback_plan=[],
        )
        result = ControlledEvolutionGovernor.apply_proposal(
            proposal=prop,
            target_root=".",
            authorized_by_human=True,
        )
        self.assertFalse(result.is_successful)
        self.assertEqual(result.approval_class, ApprovalClass.CORE_IMMUTABLE_DENIED)
        self.assertEqual(result.final_state, ProposalApprovalState.REJECTED)

    def test_apply_governance_required_blocks_without_human_auth(self):
        """Applying GOVERNANCE_REQUIRED proposal without human authorization blocks at REVIEWED state."""
        prop = StructuredCapabilityProposal(
            proposal_id="prop-need-auth",
            gap_id="gap-6",
            proposal_type=StructuredProposalType.ADD_PROJECT_SKILL,
            evidence={},
            rationale="create skill",
            alternatives=[],
            selected_option="",
            risk_tier="MEDIUM",
            blast_radius=["skills"],
            affected_paths=[".agents/skills/db-skill/SKILL.md"],
            required_tools=[],
            required_skills=[],
            required_agents=[],
            verification_plan=[],
            rollback_plan=[],
            approval_state=ProposalApprovalState.PROPOSED,
        )
        result = ControlledEvolutionGovernor.apply_proposal(
            proposal=prop,
            target_root=".",
            authorized_by_human=False,
        )
        self.assertFalse(result.is_successful)
        self.assertEqual(result.final_state, ProposalApprovalState.REVIEWED)
        self.assertIn("Human governance sign-off required", result.rationale)

    def test_snapshot_and_successful_application_in_tempdir(self):
        """Verify pre-application snapshotting, file emission, and manifest bump."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            cfg_file = root / "antios.config.json"
            cfg_file.write_text('{"initial": true}', encoding="utf-8")

            # Create initial manifest
            manifest = ProjectManifest(
                schema_version="2.0.0",
                antios_version="2.0.0",
                project_fingerprint="test-fp-1234",
                source_revision="v2.0.0",
                capability_revision="1.0",
            )
            save_manifest(manifest, root)

            prop = StructuredCapabilityProposal(
                proposal_id="prop-apply-ok",
                gap_id="gap-7",
                proposal_type=StructuredProposalType.ADD_TOOL_ADAPTER,
                evidence={},
                rationale="update config",
                alternatives=[],
                selected_option="",
                risk_tier="LOW",
                blast_radius=["config"],
                affected_paths=["antios.config.json"],
                required_tools=[],
                required_skills=[],
                required_agents=[],
                verification_plan=[],
                rollback_plan=[],
            )

            result = ControlledEvolutionGovernor.apply_proposal(
                proposal=prop,
                target_root=root,
                authorized_by_human=False, # AUTO_EXECUTABLE does not require human auth
                file_contents={"antios.config.json": '{"updated": true}'},
            )

            self.assertTrue(result.is_successful)
            self.assertEqual(result.final_state, ProposalApprovalState.VERIFIED)
            self.assertEqual(result.applied_files, ["antios.config.json"])
            self.assertEqual(cfg_file.read_text(encoding="utf-8"), '{"updated": true}')

            updated_man = load_manifest(root)
            self.assertIsNotNone(updated_man)
            self.assertEqual(updated_man.capability_revision, "1.1")


if __name__ == "__main__":
    unittest.main()
