"""Unit and integration tests for AntiOS 2.0 Mission State Continuity (Phase 89)."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from framework.core.mission_state import (
    MissionLifecycleState,
    MissionPersistenceMode,
    MissionRecoveryAction,
    MissionRecoveryDecision,
    MissionRecoveryEngine,
    MissionState,
    MissionStateStore,
    ToolOutputClassification,
    ToolOutputClassifier,
    ToolOutputEvidence,
)


class TestMissionStateContinuity(unittest.TestCase):
    """Test suite verifying bounded mission state persistence, lifecycle, and recovery."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_trivial_task_evaluates_to_ephemeral(self):
        """Single-file, single-wave, LOW-risk SOLO tasks use ephemeral in-memory state."""
        mode = MissionStateStore.evaluate_persistence_threshold(
            task_intent="Fix spelling typo in README",
            file_count=1,
            wave_count=1,
            risk_tier="LOW",
            workforce_mode="SOLO",
        )
        self.assertEqual(mode, MissionPersistenceMode.EPHEMERAL)

    def test_complex_task_evaluates_to_persistent(self):
        """Multi-file or multi-wave or HIGH-risk tasks mandate persistent disk state."""
        # Multi-file task
        mode_multi = MissionStateStore.evaluate_persistence_threshold(
            task_intent="Refactor database adapters and add tests",
            file_count=4,
            wave_count=3,
            risk_tier="MEDIUM",
            workforce_mode="PARALLEL",
        )
        self.assertEqual(mode_multi, MissionPersistenceMode.PERSISTENT)

        # High-risk task
        mode_high_risk = MissionStateStore.evaluate_persistence_threshold(
            task_intent="Modify authentication hook",
            file_count=1,
            wave_count=1,
            risk_tier="HIGH",
            workforce_mode="SOLO",
        )
        self.assertEqual(mode_high_risk, MissionPersistenceMode.PERSISTENT)

    def test_save_and_load_persistent_mission_four_files(self):
        """Persistent mission creates exactly the 4 canonical JSON files and restores state."""
        state = MissionState(
            mission_id="mission-4200",
            objective="Migrate cache layer to redis",
            acceptance_criteria=["Redis client configured", "Cache tests pass"],
            risk_tier="MEDIUM",
            current_state=MissionLifecycleState.ACTIVE,
            current_wave=2,
            active_workstreams=["backend-redis", "unit-tests"],
            completed_workstreams=["redis-schema"],
            pending_workstreams=["benchmarks"],
            decisions=["ADR-42: Use Redis 7 with cluster support"],
            evidence_refs=[{"test": "test_redis.py", "exit_code": 0}],
            handoff_refs=[{"worker": "worker-1", "status": "COMPLETED"}],
            verification_state="PENDING",
            learning_refs=["obs-123"],
            project_fingerprint="sha256:fingerprint_abc",
            active_agents=[{"agent_id": "subagent-1", "role": "Redis Engineer"}],
            total_spawned_agents=3,
        )

        m_dir = MissionStateStore.save_mission(state, workspace_root=self.temp_dir)
        self.assertTrue((m_dir / "mission.json").is_file())
        self.assertTrue((m_dir / "progress.json").is_file())
        self.assertTrue((m_dir / "evidence.json").is_file())
        self.assertTrue((m_dir / "handoffs.json").is_file())

        # Load back
        loaded = MissionStateStore.load_mission("mission-4200", workspace_root=self.temp_dir)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.mission_id, "mission-4200")
        self.assertEqual(loaded.current_wave, 2)
        self.assertEqual(loaded.total_spawned_agents, 3)
        self.assertEqual(loaded.active_workstreams, ["backend-redis", "unit-tests"])
        self.assertEqual(loaded.decisions, ["ADR-42: Use Redis 7 with cluster support"])
        self.assertEqual(loaded.learning_refs, ["obs-123"])

    def test_crash_recovery_detects_interrupted_wave_workers(self):
        """Recovery detects active worker remnants from interrupted wave and prompts RESUME."""
        state = MissionState(
            mission_id="mission-9999",
            objective="Interrupted parallel refactor",
            acceptance_criteria=["Pass tests"],
            risk_tier="MEDIUM",
            current_state=MissionLifecycleState.ACTIVE,
            current_wave=2,
            active_agents=[
                {"agent_id": "worker-a", "role": "Frontend Specialist"},
                {"agent_id": "worker-b", "role": "Backend Specialist"},
            ],
            total_spawned_agents=4,
            project_fingerprint="sha256:same_fp",
        )
        MissionStateStore.save_mission(state, workspace_root=self.temp_dir)

        decision = MissionRecoveryEngine.evaluate_recovery(
            mission_id="mission-9999",
            current_project_fingerprint="sha256:same_fp",
            workspace_root=self.temp_dir,
        )
        self.assertEqual(decision.action, MissionRecoveryAction.RESUME)
        self.assertEqual(len(decision.active_agent_remnants), 2)
        self.assertEqual(decision.reconciled_wave, 2)

    def test_crash_recovery_detects_fingerprint_mismatch_and_refreshes(self):
        """Manifest drift during interruption triggers REFRESH action."""
        state = MissionState(
            mission_id="mission-7777",
            objective="Ongoing mission",
            acceptance_criteria=["Pass"],
            risk_tier="LOW",
            current_state=MissionLifecycleState.ACTIVE,
            current_wave=1,
            project_fingerprint="sha256:old_fingerprint",
        )
        MissionStateStore.save_mission(state, workspace_root=self.temp_dir)

        decision = MissionRecoveryEngine.evaluate_recovery(
            mission_id="mission-7777",
            current_project_fingerprint="sha256:drifted_fingerprint",
            workspace_root=self.temp_dir,
        )
        self.assertEqual(decision.action, MissionRecoveryAction.REFRESH)
        self.assertTrue(decision.is_fingerprint_mismatch)

    def test_missing_or_corrupted_mission_aborts(self):
        """Non-existent mission evaluates to ABORT."""
        decision = MissionRecoveryEngine.evaluate_recovery(
            mission_id="non-existent",
            workspace_root=self.temp_dir,
        )
        self.assertEqual(decision.action, MissionRecoveryAction.ABORT)

    def test_tool_output_classifier_bounds_oversized_stdout(self):
        """Large tool output (> 2,000 chars) is compacted into bounded excerpt with SHA-256."""
        huge_stdout = "Test line pass: OK\n" * 200  # ~3800 chars
        evidence = ToolOutputClassifier.process_output(
            tool_name="run_command",
            command_or_path="pytest",
            stdout=huge_stdout,
            exit_code=0,
        )
        self.assertEqual(evidence.classification, ToolOutputClassification.SUMMARIZED)
        self.assertLessEqual(len(evidence.compact_summary.splitlines()), 25)
        self.assertTrue(len(evidence.raw_sha256) == 64)
        self.assertIn("truncated", evidence.compact_summary)

    def test_tool_output_classifier_keeps_short_output_relevant(self):
        """Short tool output (<= 2,000 chars) is preserved as RELEVANT."""
        short_stdout = "Ran 12 tests in 0.2s: OK"
        evidence = ToolOutputClassifier.process_output(
            tool_name="run_command",
            command_or_path="pytest tests/unit",
            stdout=short_stdout,
            exit_code=0,
        )
        self.assertEqual(evidence.classification, ToolOutputClassification.RELEVANT)
        self.assertEqual(evidence.compact_summary, short_stdout)

    def test_archive_mission_transitions_state(self):
        """Archiving a mission changes current_state to ARCHIVED."""
        state = MissionState(
            mission_id="mission-done",
            objective="Completed task",
            acceptance_criteria=["Done"],
            risk_tier="LOW",
            current_state=MissionLifecycleState.COMPLETED,
        )
        MissionStateStore.save_mission(state, workspace_root=self.temp_dir)
        ok = MissionStateStore.archive_mission("mission-done", workspace_root=self.temp_dir)
        self.assertTrue(ok)

        reloaded = MissionStateStore.load_mission("mission-done", workspace_root=self.temp_dir)
        self.assertEqual(reloaded.current_state, MissionLifecycleState.ARCHIVED)


if __name__ == "__main__":
    unittest.main()
