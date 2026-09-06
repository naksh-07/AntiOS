"""Unit & Integration Tests for AntiOS 2.0 Long-Horizon Adaptive Engineering (Phase 98)."""

import os
import shutil
import tempfile
import unittest

from framework.core.long_horizon import (
    ComparisonOutcome,
    ExecutionMode,
    LongHorizonEvaluationEngine,
    LongHorizonSequenceId,
    LongHorizonSequenceReport,
    LongHorizonStepResult,
)
from framework.core.mission_benchmark import BenchmarkProxyMetric
from framework.core.project_proof import (
    EvidenceDistillationEngine,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
)
from framework.core.evidence import EvidenceItem, EpistemicCategory, EvidenceState
from framework.core.release_certification import CertificationLevel


class TestLongHorizonEvaluationEngine(unittest.TestCase):
    """Tests for Phase 98 Long-Horizon Adaptive Engineering Evaluation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_long_horizon_suite_")
        self.engine = LongHorizonEvaluationEngine(workspace_root=self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_01_evolution_and_wayfinding_improvement(self):
        report = self.engine.execute_sequence(
            LongHorizonSequenceId.RUN_01,
            execution_mode=ExecutionMode.SIMULATED_TRACE,
        )
        self.assertIsInstance(report, LongHorizonSequenceReport)
        self.assertEqual(report.sequence_id, LongHorizonSequenceId.RUN_01)
        self.assertEqual(report.total_steps, 4)
        self.assertEqual(report.passed_steps, 3)
        self.assertEqual(report.comparison_outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)
        self.assertTrue(report.knowledge_reuse_validated)
        self.assertEqual(report.certification_level, CertificationLevel.CERTIFIED)

        # Before vs After delta metrics
        self.assertGreater(report.metrics_delta["time_to_correct_location"], 0)
        self.assertGreater(report.metrics_delta["unnecessary_files_inspected"], 0)
        self.assertGreater(report.metrics_delta["cost_proxy_delta"], 0)

    def test_run_02_discovery_and_staged_delivery(self):
        report = self.engine.execute_sequence(
            LongHorizonSequenceId.RUN_02,
            execution_mode=ExecutionMode.SIMULATED_TRACE,
        )
        self.assertEqual(report.sequence_id, LongHorizonSequenceId.RUN_02)
        self.assertEqual(report.total_steps, 3)
        self.assertEqual(report.passed_steps, 3)
        self.assertEqual(report.certification_level, CertificationLevel.CERTIFIED)

    def test_run_03_physical_mutation_and_proof_invalidation(self):
        report = self.engine.execute_sequence(
            LongHorizonSequenceId.RUN_03,
            execution_mode=ExecutionMode.SIMULATED_TRACE,
        )
        self.assertEqual(report.sequence_id, LongHorizonSequenceId.RUN_03)
        self.assertEqual(report.total_steps, 2)
        self.assertGreaterEqual(report.metrics_delta.get("invalidated_proofs", 0), 1)
        self.assertEqual(report.certification_level, CertificationLevel.CERTIFIED)

    def test_run_04_worker_failure_recovery_and_continuation(self):
        report = self.engine.execute_sequence(
            LongHorizonSequenceId.RUN_04,
            execution_mode=ExecutionMode.SIMULATED_TRACE,
        )
        self.assertEqual(report.sequence_id, LongHorizonSequenceId.RUN_04)
        self.assertEqual(report.total_steps, 2)
        self.assertEqual(report.passed_steps, 2)
        self.assertEqual(report.certification_level, CertificationLevel.CERTIFIED)

    def test_run_05_conflicting_evidence_resolution(self):
        report = self.engine.execute_sequence(
            LongHorizonSequenceId.RUN_05,
            execution_mode=ExecutionMode.SIMULATED_TRACE,
        )
        self.assertEqual(report.sequence_id, LongHorizonSequenceId.RUN_05)
        self.assertEqual(report.total_steps, 2)
        self.assertEqual(report.passed_steps, 1)
        self.assertEqual(report.certification_level, CertificationLevel.CERTIFIED)

    def test_unvalidated_agent_guess_cannot_enter_durable_proofs(self):
        # Epistemic defense test: raw agent speculation/guess rejected
        proof_store = ProjectProofStore(self.temp_dir)
        initial_count = len(proof_store.list_proofs())

        with self.assertRaises(Exception):
            # Attempting to distill from INFERENCE category or empty evidence
            bad_item = EvidenceItem(
                evidence_id="ev-bad",
                mission_id="m-bad",
                intent="agent guess",
                provenance="agent_speculation",
                epistemic_category=EpistemicCategory.INFERENCE,
                worker_identity="Agent Speculator",
            )
            EvidenceDistillationEngine.distill_proof(
                evidence_item=bad_item,
                subject=ProofSubject.VERIFIED_COMMAND,
                statement="I think this will pass",
                project_fingerprint="fp-bad",
                workspace_root=self.temp_dir,
            )

        self.assertEqual(len(proof_store.list_proofs()), initial_count)

    def test_invalidated_proof_excluded_from_build_context(self):
        # Verification that verify_physical_reality demotes stale proofs and excludes them
        proof_store = ProjectProofStore(self.temp_dir)
        test_file = os.path.join(self.temp_dir, "tracked.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("x = 1\n")

        proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=EvidenceItem(
                evidence_id="ev-tracked",
                mission_id="m-tracked",
                intent="track file",
                provenance="verifier",
                epistemic_category=EpistemicCategory.EVIDENCE,
                state=EvidenceState.VERIFIED,
                commands_executed=["cat"],
                command_exit_codes={"cat": 0},
                test_results=[{"command": "cat", "passed": True}],
                payload={"artifact_hashes": {"tracked.py": "init-hash"}},
            ),
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="tracked.py exists with x=1",
            project_fingerprint="fp-1",
            workspace_root=self.temp_dir,
            tracked_paths=["tracked.py"],
        )
        proof.content_hash = "init-hash"
        proof.status = ProofStatus.DURABLE
        proof_store.add_or_update_proof(proof)

        # Mutate file -> demoted to INVALIDATED
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("x = 9999\n")

        proof_store.verify_physical_reality()
        p = proof_store.get_proof(proof.proof_id)
        self.assertEqual(p.status, ProofStatus.INVALIDATED)

        # Validated list excludes INVALIDATED proof
        active_proofs = [pr for pr in proof_store.list_proofs() if pr.status in (ProofStatus.DURABLE, ProofStatus.VALIDATED)]
        self.assertEqual(len(active_proofs), 0)


if __name__ == "__main__":
    unittest.main()
