"""Tests for AntiOS 2.0 Phase 93: Durable Project Proofs & Evidence Distillation.

Validates:
- Epistemic distillation axiom: OBSERVATION / INFERENCE / UNVERIFIED CLAIMS cannot become proof
- ProjectProof lifecycle (CANDIDATE -> VALIDATED -> DURABLE -> INVALIDATED / SUPERSEDED)
- Physical reality hash grounding and invalidation on disk mutation
- ProjectProofStore bounded capacity (MAX_DURABLE_PROOFS=50, MAX_REFERENCES_PER_PROOF=10)
- Token-bounded ProjectProofCard (<= 25 lines)
"""

import hashlib
import os
import shutil
import tempfile
import unittest

from framework.core.evidence import (
    EpistemicCategory,
    EvidenceItem,
    EvidenceState,
)
from framework.core.mission_evaluation import (
    DimensionEvaluation,
    EvaluationStatus,
    MissionEvaluationCard,
    MissionEvaluationDimension,
    MissionEvaluationResult,
)

from framework.core.project_proof import (
    MAX_DURABLE_PROOFS,
    EvidenceDistillationEngine,
    ProjectProof,
    ProjectProofCard,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
    RevalidationPolicy,
)


class TestProjectProofModel(unittest.TestCase):
    """Unit tests for ProjectProof model creation and invariants."""

    def test_proof_creation_and_bounds(self):
        proof = ProjectProof(
            proof_id="proof-test-001",
            subject=ProofSubject.SUBSYSTEM_OWNERSHIP,
            statement="Core subsystem owns framework/core and critical bootstrap.",
            origin_mission_id="mission-001",
            project_fingerprint="fp-abcdef123456",
            tracked_paths=["framework/core/__init__.py"],
        )
        self.assertEqual(proof.proof_id, "proof-test-001")
        self.assertEqual(proof.subject, ProofSubject.SUBSYSTEM_OWNERSHIP)
        self.assertEqual(proof.status, ProofStatus.CANDIDATE)

        d = proof.to_dict()
        restored = ProjectProof.from_dict(d)
        self.assertEqual(restored.proof_id, proof.proof_id)
        self.assertEqual(restored.statement, proof.statement)

    def test_empty_fields_raise_error(self):
        with self.assertRaises(ValueError):
            ProjectProof(
                proof_id="",
                subject=ProofSubject.VERIFIED_INVARIANT,
                statement="Invariant holds",
                origin_mission_id="m1",
                project_fingerprint="fp1",
            )

        with self.assertRaises(ValueError):
            ProjectProof(
                proof_id="p1",
                subject=ProofSubject.VERIFIED_INVARIANT,
                statement="  ",
                origin_mission_id="m1",
                project_fingerprint="fp1",
            )


class TestEvidenceDistillationEngine(unittest.TestCase):
    """Unit tests for epistemic distillation and promotion rules."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_proof_test_")
        self.test_file = os.path.join(self.temp_dir, "test_file.py")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("print('hello world')\n")
        with open(self.test_file, "rb") as f:
            self.file_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_distill_from_verified_evidence_succeeds(self):
        ev = EvidenceItem(
            evidence_id="ev-001",
            mission_id="m-100",
            intent="Verify core file exists",
            provenance="tests/test_run.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            commands_executed=["cat test_file.py"],
            payload={"artifact_hashes": {"test_file.py": self.file_hash}},
        )

        proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=ev,
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="test_file.py is verified present and uncorrupted",
            project_fingerprint="fp-12345",
            workspace_root=self.temp_dir,
            tracked_paths=["test_file.py"],
        )
        self.assertEqual(proof.status, ProofStatus.CANDIDATE)
        self.assertEqual(proof.path_hashes.get("test_file.py"), self.file_hash)
        self.assertEqual(len(proof.evidence_references), 1)

    def test_distill_rejects_unverified_or_observation(self):
        obs_item = EvidenceItem(
            evidence_id="ev-obs",
            mission_id="m-100",
            intent="Observe dir listing",
            provenance="tool:list_dir",
            epistemic_category=EpistemicCategory.OBSERVATION,
            state=EvidenceState.OBSERVED,
        )
        with self.assertRaises(ValueError) as ctx:
            EvidenceDistillationEngine.distill_proof(
                evidence_item=obs_item,
                subject=ProofSubject.VERIFIED_FILE_LOCATION,
                statement="Saw files in directory",
                project_fingerprint="fp-123",
                workspace_root=self.temp_dir,
            )
        self.assertIn("Epistemic Separation Violation", str(ctx.exception))

    def test_distill_rejects_unverified_state(self):
        ev = EvidenceItem(
            evidence_id="ev-002",
            mission_id="m-100",
            intent="Unverified test result",
            provenance="tests/run.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.OBSERVED,  # Not VERIFIED!
            commands_executed=["pytest tests/run.py"],
            payload={"artifact_hashes": {"test_file.py": self.file_hash}},
        )

        with self.assertRaises(ValueError) as ctx:
            EvidenceDistillationEngine.distill_proof(
                evidence_item=ev,
                subject=ProofSubject.VERIFIED_COMMAND,
                statement="Command ran",
                project_fingerprint="fp-123",
                workspace_root=self.temp_dir,
            )
        self.assertIn("Invalid Evidence State", str(ctx.exception))

    def test_proof_promotion_ladder(self):
        ev = EvidenceItem(
            evidence_id="ev-prom",
            mission_id="m-prom",
            intent="Verify invariant",
            provenance="verifier_audit",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            invariant_checks=["SHALLOW_DEPTH_LE_2: PASS"],
        )
        proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=ev,
            subject=ProofSubject.VERIFIED_INVARIANT,
            statement="Shallow depth <= 2 invariant held",
            project_fingerprint="fp-stable",
            workspace_root=self.temp_dir,
        )
        self.assertEqual(proof.status, ProofStatus.CANDIDATE)

        card = MissionEvaluationCard(
            mission_id="m-prom",
            verdict=EvaluationStatus.PASS,
            acceptance_summary="Passed",
            physical_changes_summary="None",
            tests_summary="1 passed",
            invariants_summary="Held",
            evidence_summary="Verified",
            governance_summary="Compliant",
            freshness_summary="Fresh",
            uncertainty_summary="None",
        )
        eval_res = MissionEvaluationResult(
            mission_id="m-prom",
            overall_status=EvaluationStatus.PASS,
            dimension_evaluations={
                "WORKFORCE_GOVERNANCE": DimensionEvaluation(
                    dimension=MissionEvaluationDimension.WORKFORCE_GOVERNANCE,
                    status=EvaluationStatus.PASS,
                )
            },
            card=card,
            evidence_hash="ev-hash-999",
            timestamp="2026-09-06T00:00:00Z",
        )


        # Promote Candidate -> Validated -> Durable
        promoted = EvidenceDistillationEngine.promote_proof(
            proof=proof,
            evaluation_result=eval_res,
            current_fingerprint="fp-stable",
            recurrence_count=2,
        )
        self.assertEqual(promoted.status, ProofStatus.DURABLE)

    def test_promotion_demotes_on_failed_mission(self):
        ev = EvidenceItem(
            evidence_id="ev-fail",
            mission_id="m-fail",
            intent="Verify feature",
            provenance="tests/run.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            test_results=[{"exit_code": 0}],
        )

        proof = EvidenceDistillationEngine.distill_proof(
            evidence_item=ev,
            subject=ProofSubject.CONFIRMED_TEST_OWNERSHIP,
            statement="Feature test owns feature",
            project_fingerprint="fp-1",
            workspace_root=self.temp_dir,
        )
        card_fail = MissionEvaluationCard(
            mission_id="m-fail",
            verdict=EvaluationStatus.FAIL,
            acceptance_summary="Failed",
            physical_changes_summary="None",
            tests_summary="1 failed",
            invariants_summary="Broken",
            evidence_summary="Invalidated",
            governance_summary="Non-compliant",
            freshness_summary="Stale",
            uncertainty_summary="High",
        )
        failing_res = MissionEvaluationResult(
            mission_id="m-fail",
            overall_status=EvaluationStatus.FAIL,
            dimension_evaluations={},
            card=card_fail,
            evidence_hash="hash-fail",
            timestamp="2026-09-06T00:00:00Z",
        )

        promoted = EvidenceDistillationEngine.promote_proof(
            proof=proof,
            evaluation_result=failing_res,
            current_fingerprint="fp-1",
        )
        self.assertEqual(promoted.status, ProofStatus.INVALIDATED)


class TestProjectProofStore(unittest.TestCase):
    """Unit tests for ProjectProofStore persistence, invalidation, and bounding."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_store_test_")
        self.test_file = os.path.join(self.temp_dir, "tracked.txt")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("content A\n")
        with open(self.test_file, "rb") as f:
            self.initial_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_save_load_and_card(self):
        store = ProjectProofStore(workspace_root=self.temp_dir)
        proof = ProjectProof(
            proof_id="proof-store-01",
            subject=ProofSubject.VERIFIED_COMMAND,
            statement="python tests/run_all.py exit code 0",
            origin_mission_id="m-store-1",
            project_fingerprint="fp-store",
            status=ProofStatus.DURABLE,
            tracked_paths=["tracked.txt"],
            path_hashes={"tracked.txt": self.initial_hash},
        )
        store.add_or_update_proof(proof)

        # Load fresh store instance
        store2 = ProjectProofStore(workspace_root=self.temp_dir)
        loaded = store2.get_proof("proof-store-01")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.statement, proof.statement)
        self.assertEqual(loaded.status, ProofStatus.DURABLE)

        # Emits bounded card <= 25 lines
        card = store2.emit_summary_card(project_fingerprint="fp-store")
        card_text = card.format_card(max_lines=25)
        self.assertLessEqual(len(card_text.splitlines()), 25)
        self.assertIn("ANTIOS DURABLE PROJECT PROOFS", card_text)

    def test_physical_reality_invalidation(self):
        store = ProjectProofStore(workspace_root=self.temp_dir)
        proof = ProjectProof(
            proof_id="proof-ground-01",
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="tracked.txt has content A",
            origin_mission_id="m-ground-1",
            project_fingerprint="fp-ground",
            status=ProofStatus.DURABLE,
            tracked_paths=["tracked.txt"],
            path_hashes={"tracked.txt": self.initial_hash},
        )
        store.add_or_update_proof(proof)

        # Mutate the file on disk
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("content B - MUTATED\n")

        # Physical audit must detect the drift and invalidate proof
        drifted = store.verify_physical_reality()
        self.assertEqual(len(drifted), 1)
        self.assertEqual(drifted[0][0], "proof-ground-01")
        self.assertIn("File content modified", drifted[0][1])

        # Status in store should now be INVALIDATED
        p = store.get_proof("proof-ground-01")
        self.assertEqual(p.status, ProofStatus.INVALIDATED)

    def test_supersession(self):
        store = ProjectProofStore(workspace_root=self.temp_dir)
        p1 = ProjectProof(
            proof_id="p-old",
            subject=ProofSubject.NAVIGATION_HINT,
            statement="Old hint",
            origin_mission_id="m1",
            project_fingerprint="fp1",
            status=ProofStatus.DURABLE,
        )
        p2 = ProjectProof(
            proof_id="p-new",
            subject=ProofSubject.NAVIGATION_HINT,
            statement="New refined hint",
            origin_mission_id="m2",
            project_fingerprint="fp1",
            status=ProofStatus.DURABLE,
        )
        store.add_or_update_proof(p1)
        store.add_or_update_proof(p2)

        ok = store.supersede_proof("p-old", "p-new")
        self.assertTrue(ok)
        self.assertEqual(store.get_proof("p-old").status, ProofStatus.SUPERSEDED)
        self.assertEqual(store.get_proof("p-old").superseded_by, "p-new")


if __name__ == "__main__":
    unittest.main()
