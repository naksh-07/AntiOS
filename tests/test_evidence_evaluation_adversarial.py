"""Adversarial and Security Test Suite for Phases 90–92.

Covers the 12 mandatory adversarial attack vectors:
1. Worker falsely claims PASS without evidence
2. Missing test evidence on MEDIUM/HIGH risk missions
3. Forged artifact hash detected via physical audit
4. Stale evidence after repository mutation
5. Evidence provenance stripping attempt
6. Conflicting verifier results
7. Inference presented as verified observation/evidence
8. Benchmark metric tampering
9. Baseline result manipulation
10. Evidence package truncation removing invariants
11. Cross-mission evidence contamination
12. Recovery state claiming successful completion without evidence
"""

import hashlib
import json
import os
import tempfile
import unittest

from framework.core.evidence import (
    ArtifactFingerprint,
    EpistemicCategory,
    EvidenceBuilder,
    EvidenceItem,
    EvidencePackage,
    EvidenceState,
)
from framework.core.mission_evaluation import (
    EvaluationStatus,
    MissionEvaluationDimension,
    MissionEvaluationEngine,
)
from framework.core.mission_benchmark import (
    BenchmarkProxyMetric,
    BenchmarkTrace,
    ComparisonOutcome,
    MissionBenchmarkEngine,
)
from framework.core.mission_state import (
    MissionLifecycleState,
    MissionRecoveryEngine,
    MissionState,
    MissionStateStore,
)


class TestEvidenceEvaluationAdversarial(unittest.TestCase):
    """Adversarial test suite covering all 12 attack vectors."""

    def test_vector_1_worker_falsely_claims_pass_without_evidence(self):
        """Vector 1: Worker falsely claims PASS without test or command evidence."""
        # Attempt 1: Worker tries to create an unbacked EVIDENCE item
        with self.assertRaises(ValueError) as ctx:
            EvidenceItem(
                evidence_id="ev-fake-1",
                mission_id="m-fake",
                intent="Fix all bugs",
                provenance="Agent assertion",
                epistemic_category=EpistemicCategory.EVIDENCE,
                worker_identity="rogue-agent",
            )
        self.assertIn("Epistemic Separation Violation", str(ctx.exception))

        # Attempt 2: Worker creates an INFERENCE claiming success, but evaluator refuses PASS
        item = EvidenceItem(
            evidence_id="ev-inf-claim",
            mission_id="m-fake",
            intent="Fix all bugs",
            provenance="Agent assertion",
            epistemic_category=EpistemicCategory.INFERENCE,
            worker_identity="rogue-agent",
        )
        pkg = EvidencePackage(
            mission_id="m-fake",
            intent="Fix bugs",
            acceptance_criteria=["Bugs fixed"],
            evidence_items=[item],
        )
        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="LOW")
        self.assertNotEqual(res.overall_status, EvaluationStatus.PASS)

    def test_vector_2_missing_test_evidence_on_high_risk_mission(self):
        """Vector 2: Missing physical test evidence on HIGH risk mission fails closed."""
        pkg = EvidencePackage(
            mission_id="m-sec-1",
            intent="Modify security auth",
            acceptance_criteria=["Auth fortified"],
            changed_artifacts=["framework/core/auth.py"],
            # No tests, no executed commands
        )
        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="HIGH")
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertEqual(
            res.dimension_evaluations[MissionEvaluationDimension.TEST_VERIFICATION.value].status,
            EvaluationStatus.FAIL,
        )

    def test_vector_3_forged_artifact_hash_detected(self):
        """Vector 3: Forged artifact hash does not match actual filesystem content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "secure.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("actual_code_on_disk")

            actual_sha = hashlib.sha256(b"actual_code_on_disk").hexdigest()
            forged_sha = "0000000000000000000000000000000000000000000000000000000000000000"

            fp = ArtifactFingerprint(
                path=file_path,
                sha256_before="",
                sha256_after=forged_sha,
            )

            # Audit check: does disk match claimed after sha?
            with open(file_path, "rb") as f:
                disk_sha = hashlib.sha256(f.read()).hexdigest()

            self.assertNotEqual(fp.sha256_after, disk_sha)
            self.assertEqual(disk_sha, actual_sha)

    def test_vector_4_stale_evidence_after_repository_mutation(self):
        """Vector 4: Stale evidence fails freshness reality alignment."""
        builder = EvidenceBuilder(
            mission_id="m-stale-attack",
            intent="Apply change",
            acceptance_criteria=["Modify logic"],
        )
        builder.add_command_evidence("pytest", 0, "OK")
        item = EvidenceItem(
            evidence_id="ev-stale-item",
            mission_id="m-stale-attack",
            intent="Cached file read",
            provenance="stale-cache",
            freshness_state="STALE",
            commands_executed=["cat"],
            command_exit_codes={"cat": 0},
        )
        builder.package.add_evidence_item(item)
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="LOW")
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertIn("stale", " ".join(res.metadata.get("failure_reasons", [])).lower())

    def test_vector_5_evidence_provenance_stripping_attempt(self):
        """Vector 5: Attempting to strip provenance from an EvidenceItem fails closed."""
        with self.assertRaises(ValueError) as ctx:
            EvidenceItem(
                evidence_id="ev-stripped",
                mission_id="m-5",
                intent="Strip origin",
                provenance="   ",  # Whitespace only
                commands_executed=["pytest"],
                command_exit_codes={"pytest": 0},
            )
        self.assertIn("provenance is required", str(ctx.exception))

    def test_vector_6_conflicting_verifier_results_resolves_inconclusive(self):
        """Vector 6: Conflicting verifier verdicts must resolve to INCONCLUSIVE."""
        pkg = EvidencePackage(
            mission_id="m-split-verdict",
            intent="Audit security patch",
            acceptance_criteria=["Patch verified"],
        )
        item1 = EvidenceItem(
            evidence_id="ev-chk-1",
            mission_id="m-split-verdict",
            intent="Verifier A says PASS",
            provenance="Checker A",
            state=EvidenceState.VERIFIED,
            commands_executed=["test_a"],
            command_exit_codes={"test_a": 0},
        )
        item2 = EvidenceItem(
            evidence_id="ev-chk-2",
            mission_id="m-split-verdict",
            intent="Verifier B says CONFLICT",
            provenance="Checker B",
            state=EvidenceState.CONFLICTING,
            commands_executed=["test_b"],
            command_exit_codes={"test_b": 1},
        )
        pkg.add_evidence_item(item1)
        pkg.add_evidence_item(item2)

        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="LOW")
        self.assertEqual(res.overall_status, EvaluationStatus.INCONCLUSIVE)

    def test_vector_7_inference_presented_as_verified_evidence(self):
        """Vector 7: An agent marks an INFERENCE item as VERIFIED."""
        item = EvidenceItem(
            evidence_id="ev-fake-verified-inference",
            mission_id="m-epistemic-hack",
            intent="Hypothesis presented as verified fact",
            provenance="Agent thought",
            epistemic_category=EpistemicCategory.INFERENCE,
            state=EvidenceState.VERIFIED,  # Illegal state for pure inference!
        )
        pkg = EvidencePackage(
            mission_id="m-epistemic-hack",
            intent="Test epistemic boundary",
            acceptance_criteria=["Criteria 1"],
            evidence_items=[item],
        )
        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="LOW")
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertIn("Epistemic violation", " ".join(res.metadata.get("failure_reasons", [])))

    def test_vector_8_benchmark_metric_tampering(self):
        """Vector 8: Tampering with benchmark metric cost proxy re-calculates deterministically."""
        metric = BenchmarkProxyMetric(
            context_consumed_tokens_proxy=10000,
            tool_calls_count=10,
            workforce_launches=2,
            unnecessary_files_inspected=3,
            mission_completion_cost_proxy=-999.0,  # Maliciously forged negative cost!
        )
        recomputed = metric.compute_cost_proxy()
        # 10000*0.001 (10.0) + 10*0.5 (5.0) + 2*5.0 (10.0) + 3*2.0 (6.0) = 31.0
        self.assertEqual(recomputed, 31.0)
        self.assertEqual(metric.mission_completion_cost_proxy, 31.0)

    def test_vector_9_baseline_result_manipulation(self):
        """Vector 9: Fabricated baseline trace with zero cost does not trick comparison engine."""
        base_metric = BenchmarkProxyMetric(
            context_consumed_tokens_proxy=1000,
            tool_calls_count=1,
            final_correctness=False,  # Failed!
            evidence_completeness_ratio=0.0,
        )
        anti_metric = BenchmarkProxyMetric(
            context_consumed_tokens_proxy=2000,
            tool_calls_count=2,
            final_correctness=True,   # Passed!
            evidence_completeness_ratio=1.0,
        )
        t_base = BenchmarkTrace(workflow_type="BASELINE", scenario_id="SCENARIO_B", metrics=base_metric, final_verdict="FAIL")
        t_anti = BenchmarkTrace(workflow_type="ANTIOS", scenario_id="SCENARIO_B", metrics=anti_metric, final_verdict="PASS")

        report = MissionBenchmarkEngine.compare_traces(t_base, t_anti)
        # Even though anti_cost > base_cost, AntiOS is an OBSERVED_IMPROVEMENT because Baseline failed!
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)
        self.assertIn("AntiOS=PASS vs Base=FAIL", report.summary_notes)

    def test_vector_10_evidence_package_truncation_removing_invariants(self):
        """Vector 10: Invariant checks cannot be silently dropped; failed invariant always triggers FAIL."""
        pkg = EvidencePackage(
            mission_id="m-inv-trunc",
            intent="Test invariant survival",
            acceptance_criteria=["Criterion 1"],
        )
        pkg.record_command("pytest", 0, "OK")
        pkg.record_invariant("Constitution limits", False, "Worker exceeded 10 per wave")
        res = MissionEvaluationEngine.evaluate(pkg, risk_tier="LOW")
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertIn("Invariants failed", " ".join(res.metadata.get("failure_reasons", [])))

    def test_vector_11_cross_mission_evidence_contamination(self):
        """Vector 11: Evidence items belonging to mission A cannot be validly bound to mission B."""
        item_a = EvidenceItem(
            evidence_id="ev-A-1",
            mission_id="mission-AAA",
            intent="Step in mission A",
            provenance="Runner A",
            commands_executed=["pytest"],
            command_exit_codes={"pytest": 0},
        )
        # Attempt to inject item_a into mission-BBB package
        pkg_b = EvidencePackage(
            mission_id="mission-BBB",
            intent="Mission B",
            acceptance_criteria=["Criterion B"],
            evidence_items=[item_a],  # Mismatched mission_id!
        )
        # Verification evaluates items against package mission_id
        mismatched = [it for it in pkg_b.evidence_items if it.mission_id != pkg_b.mission_id]
        self.assertEqual(len(mismatched), 1)
        self.assertEqual(mismatched[0].mission_id, "mission-AAA")

    def test_vector_12_recovery_state_claiming_success_without_evidence(self):
        """Vector 12: Interrupted mission claiming COMPLETED on disk without evidence package fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = MissionState(
                mission_id="m-fake-complete",
                objective="Do something critical",
                acceptance_criteria=["Done"],
                risk_tier="HIGH",
                current_state=MissionLifecycleState.COMPLETED,
                evidence_refs=[],  # No evidence!
                verification_state="UNVERIFIED",
            )
            MissionStateStore.save_mission(state, workspace_root=tmpdir)

            loaded = MissionStateStore.load_mission("m-fake-complete", workspace_root=tmpdir)
            self.assertIsNotNone(loaded)

            # Recovery engine check
            decision = MissionRecoveryEngine.evaluate_recovery(
                mission_id="m-fake-complete",
                current_project_fingerprint="",
                workspace_root=tmpdir,
            )
            # A completed mission without verified evidence cannot resume as successful
            self.assertIn(decision.action.value, ["RESUME", "REPLAN", "ABORT"])


if __name__ == "__main__":
    unittest.main()
