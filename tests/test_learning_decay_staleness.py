"""Tests for AntiOS 2.0 Phase 65: Knowledge Decay & Staleness Detection."""

from __future__ import annotations
import tempfile
from pathlib import Path
import unittest

from framework.core.learning import (
    CandidateLesson,
    DecayReport,
    EvolutionProposal,
    KnowledgeDecayEngine,
    KnowledgeState,
    ProposalType,
)
from framework.core.memory import KnowledgeAuthority


class TestLearningDecayStaleness(unittest.TestCase):
    """Test suite verifying deterministic detection of stale or invalidated knowledge."""

    def test_missing_referenced_files_triggers_staleness(self):
        """Verify lesson referencing files that no longer exist transitions to STALE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create one file, omit the other
            existing_file = root / "src" / "active_service.py"
            existing_file.parent.mkdir(parents=True, exist_ok=True)
            existing_file.write_text("# active code", encoding="utf-8")

            lesson = CandidateLesson(
                lesson_id="les-stale-check",
                title="Service registration in deprecated module",
                trigger_or_failure="Missing registration",
                rule_or_action="Register service in old_service.py",
                authority=KnowledgeAuthority.VALIDATED,
                related_files=["src/active_service.py", "src/deleted_old_service.py"],
                state=KnowledgeState.ACTIVE,
            )

            report = KnowledgeDecayEngine.evaluate_decay(
                lessons=[lesson],
                proposals=[],
                repo_root=root,
            )

            self.assertEqual(report.stale_count, 1)
            self.assertEqual(lesson.state, KnowledgeState.STALE)
            self.assertIn("deleted_old_service.py' no longer exists", lesson.invalidation_reason)

    def test_subsystem_removal_triggers_staleness(self):
        """Verify lesson for removed subsystem transitions to STALE when subsystem pruned from anatomy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            lesson = CandidateLesson(
                lesson_id="les-subsystem-decay",
                title="Legacy XML parser convention",
                trigger_or_failure="XML parse error",
                rule_or_action="Use legacy parser flag",
                authority=KnowledgeAuthority.VALIDATED,
                affected_subsystem="legacy-xml",
                state=KnowledgeState.ACTIVE,
            )

            current_subsystems = ["core", "api", "database"]

            report = KnowledgeDecayEngine.evaluate_decay(
                lessons=[lesson],
                proposals=[],
                repo_root=root,
                anatomy_subsystems=current_subsystems,
            )

            self.assertEqual(report.stale_count, 1)
            self.assertEqual(lesson.state, KnowledgeState.STALE)
            self.assertIn("legacy-xml' is no longer present", lesson.invalidation_reason)

    def test_historical_provenance_preserved_not_deleted(self):
        """Verify that stale knowledge preserves all provenance and evidence instead of being purged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            lesson = CandidateLesson(
                lesson_id="les-preserve",
                title="Historical pattern",
                trigger_or_failure="Trigger pattern",
                rule_or_action="Action pattern",
                authority=KnowledgeAuthority.VALIDATED,
                evidence_observation_ids=["obs-orig-1", "obs-orig-2"],
                related_files=["missing_file.py"],
                task_ids=["task-10"],
                recurrence_count=2,
                state=KnowledgeState.ACTIVE,
            )

            KnowledgeDecayEngine.evaluate_decay(
                lessons=[lesson],
                proposals=[],
                repo_root=root,
            )

            # Metadata and evidence must remain intact
            self.assertEqual(lesson.state, KnowledgeState.STALE)
            self.assertEqual(lesson.evidence_observation_ids, ["obs-orig-1", "obs-orig-2"])
            self.assertEqual(lesson.task_ids, ["task-10"])
            self.assertEqual(lesson.recurrence_count, 2)
            self.assertTrue(bool(lesson.invalidation_reason))

    def test_stale_proposals_transition_to_rejected(self):
        """Verify proposal targeting a non-existent skill artifact is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            prop = EvolutionProposal(
                proposal_id="prop-stale-target",
                proposal_type=ProposalType.SKILL_UPDATE,
                target_artifact=".agents/skills/antios-removed/SKILL.md",
                what_should_change="Update removed skill",
                why="Historical rule",
                status="PENDING_REVIEW",
            )

            report = KnowledgeDecayEngine.evaluate_decay(
                lessons=[],
                proposals=[prop],
                repo_root=root,
            )

            self.assertEqual(prop.status, "REJECTED")
            self.assertEqual(len(report.decayed_items), 1)
            self.assertIn("does not exist", report.decayed_items[0]["reason"])


if __name__ == "__main__":
    unittest.main()
