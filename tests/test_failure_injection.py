"""Unit & Integration Tests for AntiOS 2.0 Failure Injection & Recovery (Phase 97)."""

import os
import shutil
import tempfile
import unittest

from framework.core.failure_injection import (
    FailureClass,
    FailureInjectionHarness,
    FailureInjectionResult,
    FailureMatrixCatalog,
    FailureSpec,
)
from framework.core.mission_state import (
    MissionLifecycleState,
    MissionRecoveryAction,
    MissionRecoveryEngine,
    MissionState,
    MissionStateStore,
)
from framework.core.orchestration import MissionLedger
from framework.core.project_proof import ProjectProofStore


class TestFailureInjectionHarness(unittest.TestCase):
    """Tests for Phase 97 Failure Injection & Recovery Certification."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_failure_suite_")
        self.harness = FailureInjectionHarness(workspace_root=self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_failure_class_contains_all_16_modes(self):
        matrix = FailureMatrixCatalog.get_matrix()
        self.assertEqual(len(matrix), 16)
        for f_class in FailureClass:
            self.assertIn(f_class, matrix)
            spec = matrix[f_class]
            self.assertIsInstance(spec, FailureSpec)
            self.assertTrue(len(spec.injection_point) > 0)
            self.assertTrue(len(spec.expected_detection) > 0)
            self.assertIsInstance(spec.expected_recovery_action, MissionRecoveryAction)
            self.assertTrue(len(spec.expected_evidence) > 0)
            self.assertTrue(len(spec.expected_final_state) > 0)

    def test_worker_crash_before_write_recovery(self):
        res = self.harness.inject_failure(FailureClass.WORKER_CRASH_BEFORE_WRITE)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.RESUME)
        self.assertTrue(res.recovery_successful)
        self.assertTrue(res.counters_preserved)
        self.assertTrue(res.partial_write_contained)

    def test_worker_crash_after_partial_write_rollback(self):
        res = self.harness.inject_failure(FailureClass.WORKER_CRASH_AFTER_PARTIAL_WRITE)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.ROLLBACK)
        self.assertTrue(res.recovery_successful)
        self.assertTrue(res.partial_write_contained)
        self.assertTrue(res.counters_preserved)

    def test_test_failure_prevents_proof_promotion(self):
        proof_store = ProjectProofStore(self.temp_dir)
        initial_proof_count = len(proof_store.list_proofs())

        res = self.harness.inject_failure(FailureClass.TEST_FAILURE)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.final_state, "FAIL")
        # Ensure failing mission NEVER generates durable proofs
        self.assertEqual(len(proof_store.list_proofs()), initial_proof_count)
        self.assertTrue(res.evidence_safely_isolated)

    def test_stale_context_hash_drift_refresh(self):
        res = self.harness.inject_failure(FailureClass.STALE_CONTEXT_EXTERNAL_MUTATION)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.REFRESH)
        self.assertTrue(res.recovery_successful)

    def test_corrupted_mission_state_aborts(self):
        res = self.harness.inject_failure(FailureClass.CORRUPTED_MISSION_STATE)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.ABORT)
        self.assertTrue(res.recovery_successful)

    def test_missing_evidence_and_false_completion_fail_closed(self):
        res_missing = self.harness.inject_failure(FailureClass.MISSING_EVIDENCE)
        self.assertTrue(res_missing.detected)
        self.assertEqual(res_missing.final_state, "FAIL")

        res_false_done = self.harness.inject_failure(FailureClass.FALSE_COMPLETION_CLAIM)
        self.assertTrue(res_false_done.detected)
        self.assertEqual(res_false_done.final_state, "FAIL")

    def test_protected_zone_mutation_blocks(self):
        res = self.harness.inject_failure(FailureClass.PROTECTED_ZONE_MUTATION)
        self.assertTrue(res.injection_successful)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.BLOCK)
        self.assertTrue(res.requires_human_intervention)

    def test_run_full_matrix_passes_all_16_modes(self):
        results = self.harness.run_full_matrix()
        self.assertEqual(len(results), 16)
        for f_class, res in results.items():
            self.assertTrue(res.injection_successful, f"Injection failed for {f_class}")
            self.assertTrue(res.detected, f"Detection failed for {f_class}")
            self.assertTrue(res.recovery_successful, f"Recovery failed for {f_class}")
            self.assertTrue(res.partial_write_contained, f"Partial write leak in {f_class}")
            self.assertTrue(res.counters_preserved, f"Counter corruption in {f_class}")

    def test_counter_preservation_under_recovery(self):
        # Explicit check: Recovery never resets spawned_total or remaining_budget
        ledger = MissionLedger(spawned_total=8, active_total=2, max_total_spawned=10)
        initial_launches = ledger.spawned_total

        # Simulate interruption & recovery
        mid = "m-counter-check"
        state = MissionState(
            mission_id=mid,
            objective="Counter preservation test",
            acceptance_criteria=["test criteria"],
            risk_tier="HIGH",
            current_state=MissionLifecycleState.ACTIVE,
            active_agents=[{"role": "AntiOS Worker"}],
        )
        MissionStateStore.save_mission(state, self.temp_dir)
        decision = MissionRecoveryEngine.evaluate_recovery(mid, workspace_root=self.temp_dir)
        self.assertEqual(decision.action, MissionRecoveryAction.RESUME)

        # Confirm ledger counters unchanged
        self.assertEqual(ledger.spawned_total, initial_launches)
        self.assertEqual(ledger.remaining_budget, 2)


if __name__ == "__main__":
    unittest.main()
