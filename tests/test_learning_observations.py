"""Tests for AntiOS 2.0 Phase 61: Deterministic Project-Local Observation Capture."""

from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.learning import (
    EpistemicSource,
    EPISTEMIC_WEIGHTS,
    KnowledgeState,
    Observation,
    ObservationStore,
    ObservationType,
)


class TestLearningObservations(unittest.TestCase):
    """Test suite verifying bounded, structured observation capture and provenance."""

    def test_observation_creation_and_provenance(self):
        """Verify observation contains complete provenance and bounds fields."""
        obs = Observation(
            observation_id="obs-001",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-42",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Calculator add function failed on negative integers",
            content="AssertionError: -5 != 5 at test_calculator.py:45",
            affected_subsystem="math-engine",
            affected_component="calculator",
            related_files=["src/calculator.py", "tests/test_calculator.py"],
            evidence_references={"exit_code": 1, "test_count": 1},
            confidence=1.0,
            project_fingerprint="fp-abc123",
            status=KnowledgeState.ACTIVE,
            created_by="primary-engineer",
        )

        self.assertEqual(obs.observation_id, "obs-001")
        self.assertEqual(obs.epistemic_source, EpistemicSource.OBSERVED_FACT)
        self.assertEqual(obs.observation_type, ObservationType.TEST_FAILURE)
        self.assertEqual(obs.effective_weight, 1.0)
        self.assertEqual(len(obs.related_files), 2)
        self.assertEqual(obs.status, KnowledgeState.ACTIVE)

        d = obs.to_dict()
        self.assertEqual(d["observation_id"], "obs-001")
        self.assertEqual(d["epistemic_source"], "OBSERVED_FACT")

        restored = Observation.from_dict(d)
        self.assertEqual(restored.observation_id, obs.observation_id)
        self.assertEqual(restored.title, obs.title)
        self.assertEqual(restored.epistemic_source, EpistemicSource.OBSERVED_FACT)

    def test_epistemic_segregation_and_weights(self):
        """Verify strict epistemic segregation across 4 sources without conflation."""
        self.assertEqual(EPISTEMIC_WEIGHTS[EpistemicSource.OBSERVED_FACT], 1.0)
        self.assertEqual(EPISTEMIC_WEIGHTS[EpistemicSource.USER_ASSERTION], 0.9)
        self.assertEqual(EPISTEMIC_WEIGHTS[EpistemicSource.DERIVED_INFERENCE], 0.7)
        self.assertEqual(EPISTEMIC_WEIGHTS[EpistemicSource.AGENT_INTERPRETATION], 0.3)

        obs_fact = Observation(
            observation_id="obs-fact",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="t1",
            source="runner",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TASK_OUTCOME,
            title="Build passed",
            content="exit code 0",
            confidence=1.0,
        )
        obs_agent = Observation(
            observation_id="obs-agent",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="t1",
            source="agent",
            epistemic_source=EpistemicSource.AGENT_INTERPRETATION,
            observation_type=ObservationType.SPECIALIST_FINDING,
            title="Agent believes caching is broken",
            content="Hypothesis regarding cache invalidation",
            confidence=1.0,
        )

        self.assertGreater(obs_fact.effective_weight, obs_agent.effective_weight)
        self.assertAlmostEqual(obs_fact.effective_weight, 1.0)
        self.assertAlmostEqual(obs_agent.effective_weight, 0.3)

    def test_all_13_observation_types_supported(self):
        """Verify that all 13 canonical engineering observation types are recognized."""
        expected_types = {
            "TASK_OUTCOME",
            "TEST_FAILURE",
            "SUCCESSFUL_FIX",
            "USER_CORRECTION",
            "PROJECT_CONVENTION",
            "ARCHITECTURAL_DISCOVERY",
            "REPEATED_NAVIGATION_PATH",
            "TOOL_FAILURE",
            "SPECIALIST_FINDING",
            "VERIFICATION_RESULT",
            "RECOVERY_EVENT",
            "CAPABILITY_GAP",
            "REJECTED_APPROACH",
        }
        actual_types = {ot.value for ot in ObservationType}
        self.assertEqual(actual_types, expected_types)

    def test_observation_content_length_bounds(self):
        """Verify hard bounds on title (<= 120), content (<= 1000), and related files (<= 10)."""
        long_title = "A" * 200
        long_content = "B" * 2000
        excess_files = [f"file_{i}.py" for i in range(25)]

        obs = Observation(
            observation_id="obs-bounded",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="t1",
            source="test",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TASK_OUTCOME,
            title=long_title,
            content=long_content,
            related_files=excess_files,
        )

        self.assertLessEqual(len(obs.title), 120)
        self.assertLessEqual(len(obs.content), 1000)
        self.assertLessEqual(len(obs.related_files), 10)
        self.assertTrue(obs.title.endswith("..."))
        self.assertTrue(obs.content.endswith("..."))

    def test_observation_deduplication_and_reinforcement(self):
        """Verify structural deduplication reinforces existing observation instead of polluting store."""
        store = ObservationStore()

        obs1 = Observation(
            observation_id="obs-101",
            timestamp="2026-09-05T03:00:00Z",
            mission_id="task-1",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Import error in api module",
            content="No module named 'fastapi'",
            affected_subsystem="api-layer",
            affected_component="router",
            related_files=["src/api.py"],
            evidence_references={"error": "ModuleNotFoundError"},
            confidence=0.8,
        )

        res1, is_new1 = store.add_observation(obs1)
        self.assertTrue(is_new1)
        self.assertEqual(len(store.list_all()), 1)
        self.assertEqual(res1.recurrence_count, 1)

        # Duplicate observation from another task
        obs2 = Observation(
            observation_id="obs-102",
            timestamp="2026-09-05T03:10:00Z",
            mission_id="task-2",
            source="pytest",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
            observation_type=ObservationType.TEST_FAILURE,
            title="Import error in api module",
            content="No module named 'fastapi'",
            affected_subsystem="api-layer",
            affected_component="router",
            related_files=["src/api.py", "src/auth.py"],
            evidence_references={"task_id": "task-2"},
            confidence=0.8,
        )

        res2, is_new2 = store.add_observation(obs2)
        self.assertFalse(is_new2)
        self.assertEqual(len(store.list_all()), 1)
        self.assertEqual(res2.observation_id, "obs-101")
        self.assertEqual(res2.recurrence_count, 2)
        self.assertIn("src/auth.py", res2.related_files)
        self.assertIn("task_id", res2.evidence_references)

    def test_observation_store_bounds_and_eviction(self):
        """Verify observation store enforces MAX_OBSERVATIONS = 100 via deterministic eviction."""
        store = ObservationStore()

        # Add 110 observations
        for i in range(110):
            obs = Observation(
                observation_id=f"obs-{i:03d}",
                timestamp=f"2026-09-05T03:{i%60:02d}:00Z",
                mission_id=f"task-{i}",
                source="runner",
                epistemic_source=EpistemicSource.OBSERVED_FACT,
                observation_type=ObservationType.TASK_OUTCOME,
                title=f"Unique task outcome event #{i}",
                content=f"Execution summary for #{i}",
                status=KnowledgeState.RETIRED if i < 10 else KnowledgeState.ACTIVE,
            )
            store.add_observation(obs)

        # Must be capped at MAX_OBSERVATIONS (100)
        self.assertEqual(len(store.list_all()), ObservationStore.MAX_OBSERVATIONS)

    def test_observation_store_file_persistence_roundtrip(self):
        """Verify save_to_file and load_from_file roundtrip cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / ".antios" / "learning_observations.json"

            store = ObservationStore()
            store.add_observation(Observation(
                observation_id="obs-persist-1",
                timestamp="2026-09-05T03:00:00Z",
                mission_id="task-1",
                source="pytest",
                epistemic_source=EpistemicSource.OBSERVED_FACT,
                observation_type=ObservationType.SUCCESSFUL_FIX,
                title="Fixed type error",
                content="Added int type annotation",
                affected_subsystem="core",
            ))

            store.save_to_file(file_path)
            self.assertTrue(file_path.is_file())

            loaded = ObservationStore.load_from_file(file_path)
            self.assertEqual(len(loaded.list_all()), 1)
            loaded_obs = loaded.get("obs-persist-1")
            self.assertIsNotNone(loaded_obs)
            self.assertEqual(loaded_obs.title, "Fixed type error")


if __name__ == "__main__":
    unittest.main()
