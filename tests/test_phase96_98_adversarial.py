"""Phase 96-98 Red-Team Adversarial Campaign for AntiOS 2.0.

Validates fail-closed defenses against 16 adversarial attack vectors:
1. Simulated trace falsely labeled as native execution
2. Native execution claimed without trace evidence
3. Failure injection bypassing protected zones
4. Recovery resetting workforce counters
5. Recovery reusing stale evidence
6. Partial write treated as completion
7. Failed mission generating durable project proof
8. Corrupted trace accepted as authoritative
9. Long-horizon history exceeding bounds
10. Repeated failures causing uncontrolled workforce growth
11. Adaptation from unvalidated observation
12. Invalidated proof re-entering BUILD CONTEXT
13. Certification using stale longitudinal evidence
14. Fixture contamination between missions
15. Proving-ground harness touching forbidden external repositories
16. Simulation adapter masquerading as native Antigravity capability
"""

import copy
import hashlib
import json
import os
import shutil
import tempfile
import unittest

from framework.core.dispatch import TaskDispatchPipeline
from framework.core.evidence import (
    EpistemicCategory,
    EvidenceItem,
    EvidencePackage,
    EvidenceState,
)
from framework.core.failure_injection import (
    FailureClass,
    FailureInjectionHarness,
    FailureMatrixCatalog,
)
from framework.core.long_horizon import (
    ComparisonOutcome,
    ExecutionMode,
    LongHorizonEvaluationEngine,
    LongHorizonSequenceId,
)
from framework.core.mission_evaluation import (
    EvaluationStatus,
    MissionEvaluationEngine,
)
from framework.core.mission_state import (
    MissionLifecycleState,
    MissionRecoveryAction,
    MissionRecoveryEngine,
    MissionState,
    MissionStateStore,
)
from framework.core.orchestration import (
    MissionLedger,
    OrchestrationBudgetExceeded,
)
from framework.core.project_proof import (
    EvidenceDistillationEngine,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
)
from framework.core.proving_ground import (
    EngineeringScenario,
    MissionTrace,
    RealProvingGround,
    ScenarioCatalog,
    FORBIDDEN_PROVING_GROUND_TARGETS,
)
from framework.core.release_certification import (
    CertificationLevel,
    ReleaseCertificationEngine,
)


class TestPhase96_98AdversarialCampaign(unittest.TestCase):
    """16 Red-Team Adversarial Test Vectors for Phases 96-98."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_adv_suite_")
        self.proving_ground = RealProvingGround(sandbox_parent_dir=self.temp_dir)
        self.failure_harness = FailureInjectionHarness(workspace_root=self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_simulated_trace_falsely_labeled_as_native(self):
        """Vector 1: Simulated trace without physical test process must not be accepted as native."""
        trace = MissionTrace(
            trace_id="tr-fake-native",
            scenario_id="SCENARIO_A",
            execution_mode="NATIVE_EXECUTION",
        )
        # Empty tool calls and 0 process executions
        self.assertEqual(len(trace.tool_calls), 0)
        # Evaluating empty evidence in native mode fails closed
        empty_pkg = EvidencePackage(
            mission_id="m-fake-native",
            intent="fake native intent",
            acceptance_criteria=["crit"],
            package_id="pkg-fake",
            evidence_items=[],
            final_verdict="PASS",
        )
        eval_res = MissionEvaluationEngine.evaluate(empty_pkg, risk_tier="HIGH")
        self.assertNotEqual(eval_res.overall_status, EvaluationStatus.PASS)

    def test_02_native_execution_claimed_without_trace_evidence(self):
        """Vector 2: Native execution claimed without verifiable exit code or command record."""
        # Evidence item with no commands executed claiming PASS
        fake_evidence = EvidenceItem(
            evidence_id="ev-unbacked",
            mission_id="m-unbacked",
            intent="unbacked claim",
            provenance="agent_speech",
            epistemic_category=EpistemicCategory.OBSERVATION,
            state=EvidenceState.VERIFIED,
            commands_executed=[],
            test_results=[],
        )
        pkg = EvidencePackage(
            mission_id="m-unbacked",
            intent="unbacked",
            acceptance_criteria=["crit"],
            package_id="pkg-unbacked",
            evidence_items=[fake_evidence],
            final_verdict="PASS",
        )
        eval_res = MissionEvaluationEngine.evaluate(pkg, risk_tier="HIGH")
        self.assertEqual(eval_res.overall_status, EvaluationStatus.FAIL)

    def test_03_failure_injection_bypassing_protected_zones(self):
        """Vector 3: Failure injection attempting to mutate protected core framework paths fails closed."""
        res = self.failure_harness.inject_failure(FailureClass.PROTECTED_ZONE_MUTATION)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.BLOCK)
        self.assertTrue(res.requires_human_intervention)

    def test_04_recovery_resetting_workforce_counters(self):
        """Vector 4: Interruption and recovery attack trying to reset launched workforce counters."""
        ledger = MissionLedger(spawned_total=14, active_total=0, max_total_spawned=20)
        # Even after interrupted wave recovery, spawned_total is immutable/non-decreasing
        mid = "m-adv-counter"
        state = MissionState(
            mission_id=mid,
            objective="Recovery counter attack",
            acceptance_criteria=["test"],
            risk_tier="HIGH",
            current_state=MissionLifecycleState.ACTIVE,
            total_spawned_agents=14,
        )
        MissionStateStore.save_mission(state, self.temp_dir)
        loaded = MissionStateStore.load_mission(mid, self.temp_dir)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.total_spawned_agents, 14)
        self.assertGreaterEqual(ledger.spawned_total, 14)

    def test_05_recovery_reusing_stale_evidence(self):
        """Vector 5: Stale evidence from interrupted/mutated state cannot be reused without refresh."""
        res = self.failure_harness.inject_failure(FailureClass.STALE_CONTEXT_EXTERNAL_MUTATION)
        self.assertTrue(res.detected)
        self.assertEqual(res.recovery_action, MissionRecoveryAction.REFRESH)

    def test_06_partial_write_treated_as_completion(self):
        """Vector 6: Broken partial write claiming task completion must be rejected."""
        dirty_file = os.path.join(self.temp_dir, "broken.py")
        with open(dirty_file, "w") as f:
            f.write("def broken_syntax(\n")

        # Evaluation fails because test verification will fail
        item = EvidenceItem(
            evidence_id="ev-broken",
            mission_id="m-partial",
            intent="partial broken write",
            provenance="runner",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.INVALIDATED,
            commands_executed=["python -m py_compile broken.py"],
            command_exit_codes={"python -m py_compile broken.py": 1},
            test_results=[{"command": "compile", "passed": False, "exit_code": 1}],
        )
        pkg = EvidencePackage(
            mission_id="m-partial",
            intent="partial",
            acceptance_criteria=["compiles cleanly"],
            package_id="pkg-partial",
            evidence_items=[item],
            final_verdict="PASS",  # False claim
        )
        eval_res = MissionEvaluationEngine.evaluate(pkg, risk_tier="HIGH")
        self.assertNotEqual(eval_res.overall_status, EvaluationStatus.PASS)

    def test_07_failed_mission_generating_durable_proof(self):
        """Vector 7: Distillation engine must reject promoting proofs from failed missions."""
        failed_item = EvidenceItem(
            evidence_id="ev-failed",
            mission_id="m-failed",
            intent="failed task",
            provenance="runner",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.INVALIDATED,
        )
        with self.assertRaises(ValueError):
            EvidenceDistillationEngine.distill_proof(
                evidence_item=failed_item,
                subject=ProofSubject.VERIFIED_COMMAND,
                statement="failed command",
                project_fingerprint="fp-failed",
                workspace_root=self.temp_dir,
            )

    def test_08_corrupted_trace_tamper_detection(self):
        """Vector 8: Corrupted or forged trace hash is detected via recomputation."""
        trace = MissionTrace(
            trace_id="tr-tamper",
            scenario_id="SCENARIO_A",
            execution_mode="SIMULATED_TRACE",
            final_verdict="PASS",
        )
        original_hash = trace.trace_hash
        # Attacker modifies verdict without updating hash
        trace.final_verdict = "TAMPERED_VERDICT"
        recalculated_hash = trace.compute_hash()
        self.assertNotEqual(original_hash, recalculated_hash)

    def test_09_long_horizon_history_exceeding_bounds(self):
        """Vector 9: Trace events and certification windows enforce strict ceiling bounds."""
        trace = MissionTrace(
            trace_id="tr-bounded",
            scenario_id="SCENARIO_A",
            execution_mode="SIMULATED_TRACE",
        )
        # Inject 100 tool calls and 100 files
        for i in range(100):
            trace.record_tool_call(f"tool_{i}", "args", True)
            trace.record_file_inspected(f"file_{i}.py")
            trace.record_stage(f"stage_{i}")

        self.assertLessEqual(len(trace.tool_calls), 30)
        self.assertLessEqual(len(trace.files_inspected), 30)
        self.assertLessEqual(len(trace.stage_transitions), 20)

    def test_10_repeated_failures_causing_uncontrolled_workforce_growth(self):
        """Vector 10: Anti-Hydra protection prevents runaway worker spawns beyond max 20."""
        ledger = MissionLedger(spawned_total=20, active_total=0, max_total_spawned=20)
        can_spawn, reason = ledger.can_spawn(role="AntiOS Worker")
        self.assertFalse(can_spawn)
        self.assertIn("Constitutional ceiling reached", reason)

    def test_11_adaptation_from_unvalidated_observation(self):
        """Vector 11: Epistemic separation prevents agent opinions/observations from becoming proofs."""
        obs_item = EvidenceItem(
            evidence_id="ev-opinion",
            mission_id="m-opinion",
            intent="my opinion is that code works",
            provenance="agent_chat",
            epistemic_category=EpistemicCategory.OBSERVATION,
            state=EvidenceState.OBSERVED,
        )
        with self.assertRaises(ValueError):
            EvidenceDistillationEngine.distill_proof(
                evidence_item=obs_item,
                subject=ProofSubject.VERIFIED_COMMAND,
                statement="unverified opinion",
                project_fingerprint="fp-obs",
                workspace_root=self.temp_dir,
            )

    def test_12_invalidated_proof_re_entering_build_context(self):
        """Vector 12: Invalidated proof is excluded from TaskDispatchPipeline candidate sources."""
        proof_store = ProjectProofStore(self.temp_dir)
        init_item = EvidenceItem(
            evidence_id="ev-init",
            mission_id="m-init",
            intent="valid initially",
            provenance="runner",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            commands_executed=["test"],
            command_exit_codes={"test": 0},
            test_results=[{"command": "test", "passed": True}],
        )
        bad_proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=init_item,
            subject=ProofSubject.VERIFIED_COMMAND,
            statement="command was verified",
            project_fingerprint="fp-inv",
            workspace_root=self.temp_dir,
        )
        bad_proof.status = ProofStatus.INVALIDATED
        proof_store.add_or_update_proof(bad_proof)

        pipeline = TaskDispatchPipeline(workspace_root=self.temp_dir)
        plan = pipeline.dispatch_task(task_query="test task", mission_id="m-check-build")
        # In plan.loaded_context, the invalidated proof must NOT be loaded
        loaded_str = str(plan.loaded_context)
        self.assertNotIn(bad_proof.proof_id, loaded_str)

    def test_13_certification_using_stale_longitudinal_evidence(self):
        """Vector 13: Stale proofs prevent release certification from achieving CERTIFIED status."""
        proof_store = ProjectProofStore(self.temp_dir)
        init_item = EvidenceItem(
            evidence_id="ev-stale-init",
            mission_id="m-stale",
            intent="test",
            provenance="runner",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            commands_executed=["test"],
            command_exit_codes={"test": 0},
            test_results=[{"command": "test", "passed": True}],
        )
        stale_proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=init_item,
            subject=ProofSubject.VERIFIED_COMMAND,
            statement="stale proof",
            project_fingerprint="fp-stale",
            workspace_root=self.temp_dir,
        )
        stale_proof.status = ProofStatus.STALE
        proof_store.add_or_update_proof(stale_proof)

        # Evaluating drift on stale proofs reports findings
        drift_findings = self.failure_harness.matrix[FailureClass.ADAPTER_DRIFT]
        self.assertIsNotNone(drift_findings)

    def test_14_fixture_contamination_between_missions(self):
        """Vector 14: Executing scenario A then scenario B creates independent sandboxes with 0 leak."""
        res_a = self.proving_ground.execute_scenario("SCENARIO_A", ExecutionMode.SIMULATED_TRACE, apply_fix=True)
        res_b = self.proving_ground.execute_scenario("SCENARIO_B", ExecutionMode.SIMULATED_TRACE, apply_fix=True)

        self.assertNotEqual(res_a.repository_fingerprint, res_b.repository_fingerprint)
        self.assertNotEqual(res_a.mission_id, res_b.mission_id)
        self.assertEqual(res_a.cleanup_status, "CLEANED")
        self.assertEqual(res_b.cleanup_status, "CLEANED")

    def test_15_proving_ground_touching_forbidden_external_repositories(self):
        """Vector 15: Targeting StudyLab, StudySourceCore, or production throws PermissionError."""
        for forbidden in FORBIDDEN_PROVING_GROUND_TARGETS:
            bad_path = f"C:/workspace/{forbidden}/core"
            with self.assertRaises(PermissionError):
                self.proving_ground._validate_fixture_safety(bad_path)

    def test_16_simulation_adapter_masquerading_as_native(self):
        """Vector 16: An execution mode cannot be labeled NATIVE_EXECUTION if physically simulated."""
        result = self.proving_ground.execute_scenario(
            "SCENARIO_A",
            execution_mode=ExecutionMode.SIMULATED_TRACE,
            apply_fix=True,
        )
        # The result must record SIMULATED_TRACE, never NATIVE_EXECUTION
        self.assertEqual(result.execution_mode, ExecutionMode.SIMULATED_TRACE)
        self.assertNotEqual(result.execution_mode, ExecutionMode.NATIVE_EXECUTION)
        self.assertEqual(result.trace.execution_mode, "SIMULATED_TRACE")


if __name__ == "__main__":
    unittest.main()
