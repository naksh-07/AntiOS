"""Tests for AntiOS 2.0 Phases 62 & 63: Lesson Distillation & Evidence Promotion."""

from __future__ import annotations
import unittest

from framework.core.learning import (
    CandidateLesson,
    EpistemicSource,
    EvidencePromotionEngine,
    KnowledgeState,
    LessonDistiller,
    Observation,
    ObservationType,
)
from framework.core.memory import KnowledgeAuthority
from framework.core.verdict import VerificationVerdict


class TestLearningDistillationPromotion(unittest.TestCase):
    """Test suite verifying deterministic distillation of lessons and promotion gates."""

    def test_distill_causal_chain_test_failure_and_fix(self):
        """Verify that a sequence of test failure + fix produces a candidate lesson with evidence links."""
        obs_fail = Observation(
            observation_id="obs-f1",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-100",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Database connection timeout",
            content="OperationalError: connection timed out after 5000ms",
            affected_subsystem="database",
            affected_component="pool",
            related_files=["src/db.py"],
        )
        obs_fix = Observation(
            observation_id="obs-x1",
            timestamp="2026-09-05T03:05:00Z",
            mission_id="task-100",
            source="primary-engineer",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.SUCCESSFUL_FIX,
            title="Increased connection pool timeout to 15000ms",
            content="Updated pool_timeout in db config",
            affected_subsystem="database",
            affected_component="pool",
            related_files=["src/db.py"],
        )
        obs_pass = Observation(
            observation_id="obs-p1",
            timestamp="2026-09-05T03:10:00Z",
            mission_id="task-100",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.VERIFICATION_RESULT,
            title="All database tests PASS",
            content="5 passed in 1.2s",
            affected_subsystem="database",
        )

        candidates = LessonDistiller.distill_from_observations([obs_fail, obs_fix, obs_pass])
        self.assertEqual(len(candidates), 1)
        cand = candidates[0]

        # Verify candidate properties
        self.assertEqual(cand.authority, KnowledgeAuthority.CANDIDATE)
        self.assertIn("obs-f1", cand.evidence_observation_ids)
        self.assertIn("obs-x1", cand.evidence_observation_ids)
        self.assertIn("obs-p1", cand.evidence_observation_ids)
        self.assertEqual(cand.affected_subsystem, "database")
        self.assertEqual(cand.task_ids, ["task-100"])
        self.assertEqual(cand.recurrence_count, 1)

    def test_distill_user_correction(self):
        """Verify user correction distills into candidate lesson with user assertion evidence."""
        obs_user = Observation(
            observation_id="obs-u1",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-200",
            source="user",
            epistemic_source=EpistemicSource.USER_ASSERTION,
            observation_type=ObservationType.USER_CORRECTION,
            title="Always use double quotes in SQL queries",
            content="Repository convention mandates standard SQL quoting",
            affected_subsystem="database",
        )

        candidates = LessonDistiller.distill_from_observations([obs_user])
        self.assertEqual(len(candidates), 1)
        cand = candidates[0]
        self.assertEqual(cand.authority, KnowledgeAuthority.CANDIDATE)
        self.assertIn("obs-u1", cand.evidence_observation_ids)
        self.assertIn("user correction", cand.title.lower())

    def test_distill_deduplication_and_recurrence_reinforcement(self):
        """Verify duplicate failure patterns across missions reinforce candidate rather than duplicate."""
        obs_fail1 = Observation(
            observation_id="obs-f1",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-1",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Missing lockfile",
            content="Package lockfile out of sync with package.json",
            affected_subsystem="packaging",
        )
        obs_fix1 = Observation(
            observation_id="obs-x1",
            timestamp="2026-09-05T03:05:00Z",
            mission_id="task-1",
            source="agent",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.SUCCESSFUL_FIX,
            title="Run npm install to regenerate lockfile",
            content="npm install synchronized package-lock.json",
            affected_subsystem="packaging",
        )

        candidates = LessonDistiller.distill_from_observations([obs_fail1, obs_fix1])
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].recurrence_count, 1)

        # Later task encounters identical failure
        obs_fail2 = Observation(
            observation_id="obs-f2",
            timestamp="2026-09-05T04:00:00Z",
            mission_id="task-2",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Missing lockfile",
            content="Package lockfile out of sync with package.json",
            affected_subsystem="packaging",
        )
        obs_fix2 = Observation(
            observation_id="obs-x2",
            timestamp="2026-09-05T04:05:00Z",
            mission_id="task-2",
            source="agent",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.SUCCESSFUL_FIX,
            title="Run npm install to regenerate lockfile",
            content="npm install synchronized package-lock.json",
            affected_subsystem="packaging",
        )

        updated_candidates = LessonDistiller.distill_from_observations(
            observations=[obs_fail2, obs_fix2],
            existing_candidates=candidates,
        )

        # Count must remain 1, but recurrence reinforced across 2 distinct tasks
        self.assertEqual(len(updated_candidates), 1)
        cand = updated_candidates[0]
        self.assertEqual(cand.recurrence_count, 2)
        self.assertIn("task-1", cand.task_ids)
        self.assertIn("task-2", cand.task_ids)
        self.assertIn("obs-f1", cand.evidence_observation_ids)
        self.assertIn("obs-f2", cand.evidence_observation_ids)

    def test_weak_evidence_rejection_agent_belief_cannot_promote(self):
        """CRITICAL: An agent's belief or LLM inference alone must NEVER promote a lesson."""
        obs_agent = Observation(
            observation_id="obs-belief-1",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-1",
            source="agent:primary-engineer",
            epistemic_source=EpistemicSource.AGENT_INTERPRETATION,
            observation_type=ObservationType.SPECIALIST_FINDING,
            title="I think the compiler requires python 3.14",
            content="Agent speculative hypothesis",
            affected_subsystem="compiler",
        )

        cand = CandidateLesson(
            lesson_id="les-speculative",
            title="Compiler requires Python 3.14",
            trigger_or_failure="Agent speculation",
            rule_or_action="Enforce python 3.14",
            authority=KnowledgeAuthority.CANDIDATE,
            evidence_observation_ids=["obs-belief-1"],
            task_ids=["task-1"],
            recurrence_count=1,
            confidence=0.4,
        )

        auth, reason, conf = EvidencePromotionEngine.evaluate_promotion(
            candidate=cand,
            observations=[obs_agent],
        )

        # Must be rejected from promotion
        self.assertEqual(auth, KnowledgeAuthority.CANDIDATE)
        self.assertIn("Agent interpretation alone does not constitute validatable", reason)
        self.assertLessEqual(conf, 0.4)

    def test_promotion_to_validated_via_multitask_recurrence(self):
        """Verify candidate promotes to VALIDATED when backed by >= 2 distinct task recurrences."""
        obs1 = Observation(
            observation_id="obs-1",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-1",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Test failure",
            content="Failure 1",
        )
        obs2 = Observation(
            observation_id="obs-2",
            timestamp="2026-09-05T04:00:00Z",
            mission_id="task-2",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Test failure",
            content="Failure 2",
        )

        cand = CandidateLesson(
            lesson_id="les-recurring",
            title="Always initialize cache directory before running tests",
            trigger_or_failure="Missing cache dir",
            rule_or_action="Create cache dir",
            authority=KnowledgeAuthority.CANDIDATE,
            evidence_observation_ids=["obs-1", "obs-2"],
            task_ids=["task-1", "task-2"],
            recurrence_count=2,
            verified_resolution="mkdir cache",
            confidence=0.6,
        )

        auth, reason, conf = EvidencePromotionEngine.evaluate_promotion(
            candidate=cand,
            observations=[obs1, obs2],
        )

        self.assertEqual(auth, KnowledgeAuthority.VALIDATED)
        self.assertIn("multi-task recurrence", reason)
        self.assertGreaterEqual(conf, 0.75)

    def test_promotion_to_validated_via_independent_verifier(self):
        """Verify candidate promotes to VALIDATED when confirmed by independent verifier PASS."""
        obs = Observation(
            observation_id="obs-v",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-1",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Test fail",
            content="details",
        )

        cand = CandidateLesson(
            lesson_id="les-verified",
            title="Importing math requires float cast",
            trigger_or_failure="int to float error",
            rule_or_action="cast to float",
            authority=KnowledgeAuthority.CANDIDATE,
            evidence_observation_ids=["obs-v"],
            task_ids=["task-1"],
            recurrence_count=1,
            confidence=0.6,
        )

        verdict = VerificationVerdict(
            status="PASS",
            risk_tier="MEDIUM",
            same_change_set_verified=True,
            summary="All tests passed under independent verifier audit",
        )

        auth, reason, conf = EvidencePromotionEngine.evaluate_promotion(
            candidate=cand,
            observations=[obs],
            verifications=[verdict],
        )

        self.assertEqual(auth, KnowledgeAuthority.VALIDATED)
        self.assertIn("independent verifier PASS verdict", reason)

    def test_promotion_to_durable_via_three_task_recurrence(self):
        """Verify lesson promotes to DURABLE when reinforced across >= 3 distinct tasks."""
        cand = CandidateLesson(
            lesson_id="les-durable",
            title="Durable architectural pattern",
            trigger_or_failure="Repeated failure across 3 runs",
            rule_or_action="Mandatory registration before dispatch",
            authority=KnowledgeAuthority.VALIDATED,
            evidence_observation_ids=["o1", "o2", "o3"],
            task_ids=["task-1", "task-2", "task-3"],
            recurrence_count=3,
            confidence=0.75,
        )

        obs_list = [
            Observation(
                observation_id=f"o{i}",
                timestamp="2026-09-05T03:00:00Z",
                mission_id=f"task-{i}",
                source="pytest",
                epistemic_source=EpistemicSource.OBSERVED_FACT,
                observation_type=ObservationType.TEST_FAILURE,
                title=f"Event {i}",
                content="Observed",
            )
            for i in range(1, 4)
        ]

        auth, reason, conf = EvidencePromotionEngine.evaluate_promotion(
            candidate=cand,
            observations=obs_list,
        )

        self.assertEqual(auth, KnowledgeAuthority.DURABLE)
        self.assertIn("DURABLE", reason)
        self.assertGreaterEqual(conf, 0.85)


if __name__ == "__main__":
    unittest.main()
