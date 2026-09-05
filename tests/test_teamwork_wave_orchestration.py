"""Unit tests for Phase 85 Teamwork-Grade Wave Orchestration, Anti-Hydra & Persistence."""

import os
import tempfile
import unittest

from framework.core.orchestration import (
    FailureRecoveryDecision,
    FailureRecoveryEngine,
    FailureType,
    MissionLedger,
    OrchestrationBudgetExceeded,
    RecoveryAction,
    WaveManager,
    WavePersistenceEngine,
    WorkerMetadata,
    WriteSafetyEvaluator,
    WriteSafetyPolicy,
)


class TestTeamworkWaveOrchestration(unittest.TestCase):
    """Verifies Phase 85 Anti-Hydra protection, wave persistence, and recovery engines."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_worker_metadata_validation_enforces_complete_specification(self):
        """WorkerMetadata requires all mandatory fields to prevent anonymous workers."""
        valid_meta = WorkerMetadata(
            mission_id="mission-001",
            wave_id=1,
            parent_id=None,
            capability="testing",
            purpose="Run unit tests",
            write_boundary=["tests/"],
            expected_output="Test run results",
            verification_requirement="exit code 0",
        )
        valid, errs = valid_meta.validate()
        self.assertTrue(valid, f"Validation failed: {errs}")

        # Incomplete metadata fails validation
        invalid_meta = WorkerMetadata(
            mission_id="",
            wave_id=0,
            parent_id=None,
            capability="",
            purpose="",
            write_boundary=[],
            expected_output="",
            verification_requirement="",
        )
        valid, errs = invalid_meta.validate()
        self.assertFalse(valid)
        self.assertGreaterEqual(len(errs), 5)

    def test_anti_hydra_duplicate_specialist_rejected(self):
        """Spawning same role with identical goal or overlapping boundaries in same wave is rejected."""
        ledger = MissionLedger()
        meta1 = WorkerMetadata(
            mission_id="m1",
            wave_id=1,
            parent_id=None,
            capability="refactor",
            purpose="Refactor core module",
            write_boundary=["framework/core/a.py"],
            expected_output="Clean refactor",
            verification_requirement="Tests pass",
        )
        ledger.record_spawn("worker-1", role="refactorer", depth=1, wave_number=1, metadata=meta1)

        # Attempt duplicate spawn with overlapping boundary in wave 1
        meta2 = WorkerMetadata(
            mission_id="m1",
            wave_id=1,
            parent_id=None,
            capability="refactor",
            purpose="Refactor core module",
            write_boundary=["framework/core/a.py"],  # Overlap!
            expected_output="Clean refactor",
            verification_requirement="Tests pass",
        )
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            ledger.record_spawn("worker-2", role="refactorer", depth=1, wave_number=1, metadata=meta2)
        self.assertIn("Anti-Hydra", str(ctx.exception))

    def test_anti_hydra_runaway_retry_loop_blocked(self):
        """Recreating a failed role >= 2 times is rejected."""
        ledger = MissionLedger()
        # Record 2 failures for role 'explorer'
        rec1 = ledger.record_spawn("exp-1", role="explorer", depth=1, wave_number=1)
        ledger.record_termination("exp-1", failure_reason="Timeout")

        rec2 = ledger.record_spawn("exp-2", role="explorer", depth=1, wave_number=1)
        ledger.record_termination("exp-2", failure_reason="Crash")

        # Third spawn attempt for same failed role must be blocked
        can_retry, reason = ledger.can_retry("exp-2")
        self.assertFalse(can_retry)
        self.assertIn("Anti-Hydra", reason)

        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            ledger.record_spawn("exp-3", role="explorer", depth=1, wave_number=1)
        self.assertIn("Retry limit reached", str(ctx.exception))

    def test_wave_persistence_and_mission_recovery(self):
        """Wave state can be persisted to disk and recovered deterministically."""
        state = {
            "mission_id": "mission-42",
            "current_wave_index": 2,
            "total_spawned": 5,
            "active_workers": ["worker-a", "worker-b"],
            "waves": ["RECONNAISSANCE", "PLANNING", "IMPLEMENTATION"],
        }
        saved_path = WavePersistenceEngine.save_state(state, workspace_root=self.workspace)
        self.assertTrue(os.path.exists(saved_path))

        loaded = WavePersistenceEngine.load_state(workspace_root=self.workspace)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["mission_id"], "mission-42")
        self.assertEqual(loaded["current_wave_index"], 2)

        # Recover mission
        ok, summary, recovered_state = WavePersistenceEngine.recover_mission(workspace_root=self.workspace)
        self.assertTrue(ok)
        self.assertIn("Recovered mission 'mission-42'", summary)
        self.assertEqual(len(recovered_state["active_workers"]), 2)

        # Clear state
        cleared = WavePersistenceEngine.clear_state(workspace_root=self.workspace)
        self.assertTrue(cleared)
        self.assertIsNone(WavePersistenceEngine.load_state(workspace_root=self.workspace))

    def test_failure_recovery_engine_actions(self):
        """FailureRecoveryEngine routes failure classes to deterministic actions."""
        # 1. Ungrounded evidence -> RETRY_SAME_WORKER_CONTEXT
        dec = FailureRecoveryEngine.evaluate(
            worker_id="w-1",
            failure_type=FailureType.UNGROUNDED_EVIDENCE,
            consecutive_failures=0,
            can_retry_budget=True,
            error_message="No file paths found in handoff",
        )
        self.assertEqual(dec.action, RecoveryAction.RETRY_SAME_WORKER_CONTEXT)
        self.assertFalse(dec.can_consume_budget)
        self.assertIsNotNone(dec.retry_prompt)

        # 2. Crash -> SPAWN_NEW_WORKER
        dec = FailureRecoveryEngine.evaluate(
            worker_id="w-2",
            failure_type=FailureType.CRASH,
            consecutive_failures=0,
            can_retry_budget=True,
            error_message="Process terminated with exit code 1",
        )
        self.assertEqual(dec.action, RecoveryAction.SPAWN_NEW_WORKER)
        self.assertTrue(dec.can_consume_budget)

        # 3. Write collision -> TAKEOVER_DIRECT
        dec = FailureRecoveryEngine.evaluate(
            worker_id="w-3",
            failure_type=FailureType.WRITE_COLLISION,
            consecutive_failures=0,
            can_retry_budget=True,
        )
        self.assertEqual(dec.action, RecoveryAction.TAKEOVER_DIRECT)

        # 4. Consecutive failure limit reached -> FAIL_CLOSED
        dec = FailureRecoveryEngine.evaluate(
            worker_id="w-4",
            failure_type=FailureType.CRASH,
            consecutive_failures=2,
            can_retry_budget=True,
        )
        self.assertEqual(dec.action, RecoveryAction.FAIL_CLOSED)

        # 5. Budget exhausted -> TAKEOVER_DIRECT
        dec = FailureRecoveryEngine.evaluate(
            worker_id="w-5",
            failure_type=FailureType.CRASH,
            consecutive_failures=0,
            can_retry_budget=False,
        )
        self.assertEqual(dec.action, RecoveryAction.TAKEOVER_DIRECT)


if __name__ == "__main__":
    unittest.main()
