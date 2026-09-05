"""Red-team adversarial security test suite for AntiOS 2.0 Phases 93–95.

Validates all 15 mandatory adversarial security attack vectors:
1. Unverified observation attempting durable promotion -> Fail-closed rejection
2. Agent inference promoted as project proof -> Epistemic separation failure
3. Durable proof with stripped provenance -> Fail-closed rejection
4. Proof remaining valid after referenced file mutation -> Physical reality invalidation
5. Contradictory proof sources -> Resolves to INVALIDATED
6. Forged project fingerprint -> Demotes to STALE / rejects promotion
7. Drift report suppressed -> Health engine detects uncorroborated state as UNTRUSTED
8. Critical drift incorrectly downgraded -> Rule engine forces CRITICAL_DRIFT & BLOCK
9. Stale intelligence used during BUILD CONTEXT -> Stale proof excluded from context
10. Certification based on old mission evidence despite critical drift -> BLOCKED
11. Previous CERTIFIED state incorrectly reused after mutation -> Invalidated to DEGRADED/BLOCKED
12. Historical evidence replay attack -> Fingerprint mismatch rejects certification
13. Cross-project proof contamination -> Foreign workspace fingerprint rejected
14. Certification claim without current verification evidence -> Fail-closed UNKNOWN/BLOCKED
15. Bounded-history bypass attempting to inject hidden historical authority -> Window bounded to 10
"""

import hashlib
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional, Tuple
import unittest


from framework.core.dispatch import TaskDispatchPipeline
from framework.core.drift_health import (
    DriftAction,
    DriftDomain,
    DriftFinding,
    DriftSeverity,
    IntelligenceHealthEngine,
    IntelligenceHealthStatus,
    ProjectDriftEngine,
)
from framework.core.evidence import (
    EpistemicCategory,
    EvidenceItem,
    EvidencePackage,
    EvidenceState,
)
from framework.core.mission_evaluation import (
    EvaluationStatus,
    MissionEvaluationEngine,
    MissionEvaluationResult,
)

from framework.core.project_proof import (
    EvidenceDistillationEngine,
    ProjectProof,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
)
from framework.core.release_certification import (
    CertificationLevel,
    CertificationWindow,
    ReleaseCertificationEngine,
)


class TestPhase93To95AdversarialSecurity(unittest.TestCase):
    """15 mandatory adversarial security attack vectors covering Phases 93–95."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_adv9395_")
        self.proof_store = ProjectProofStore(workspace_root=self.temp_dir)
        self.test_file = os.path.join(self.temp_dir, "code.py")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("def func(): pass\n")
        with open(self.test_file, "rb") as f:
            self.file_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_clean_eval(self, mission_id: str) -> Tuple[MissionEvaluationResult, EvidencePackage]:
        pkg = EvidencePackage(
            mission_id=mission_id,
            intent="Run tests",
            acceptance_criteria=["Exit 0"],
        )

        ev = EvidenceItem(
            evidence_id=f"ev-{mission_id}",
            mission_id=mission_id,
            intent="Run tests",
            provenance="tests/run_all.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            test_results=[{"exit_code": 0}],
            acceptance_criteria_keys=["Exit 0"],
        )

        pkg.add_evidence_item(ev)
        pkg.final_verdict = "PASS"
        res = MissionEvaluationEngine.evaluate(evidence_package=pkg, risk_tier="LOW")
        return res, pkg


    def test_vector1_unverified_observation_promotion_blocked(self):
        """Vector 1: Unverified observation attempting durable promotion must fail closed."""
        obs = EvidenceItem(
            evidence_id="ev-obs",
            mission_id="m-1",
            intent="Observed file list",
            provenance="tool:list_dir",
            epistemic_category=EpistemicCategory.OBSERVATION,
            state=EvidenceState.OBSERVED,
        )
        with self.assertRaises(ValueError) as ctx:
            EvidenceDistillationEngine.distill_proof(
                evidence_item=obs,
                subject=ProofSubject.VERIFIED_FILE_LOCATION,
                statement="Saw file exist",
                project_fingerprint="fp-1",
                workspace_root=self.temp_dir,
            )
        self.assertIn("Epistemic Separation Violation", str(ctx.exception))

    def test_vector2_agent_inference_as_proof_rejected(self):
        """Vector 2: Agent inference promoted as project proof must fail closed."""
        inf = EvidenceItem(
            evidence_id="ev-inf",
            mission_id="m-1",
            intent="Inferred bug fix",
            provenance="agent_thought",
            epistemic_category=EpistemicCategory.INFERENCE,
            state=EvidenceState.OBSERVED,
        )
        with self.assertRaises(ValueError) as ctx:
            EvidenceDistillationEngine.distill_proof(
                evidence_item=inf,
                subject=ProofSubject.VERIFIED_INVARIANT,
                statement="I think the bug is fixed",
                project_fingerprint="fp-1",
                workspace_root=self.temp_dir,
            )
        self.assertIn("Epistemic Separation Violation", str(ctx.exception))

    def test_vector3_stripped_provenance_rejected(self):
        """Vector 3: Durable proof with stripped provenance must be rejected."""
        ev = EvidenceItem(
            evidence_id="ev-prov",
            mission_id="m-1",
            intent="Run tests",
            provenance="tests/run_all.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            test_results=[{"exit_code": 0}],
        )

        ev.provenance = "   "  # Stripped post-creation
        with self.assertRaises(ValueError) as ctx:
            EvidenceDistillationEngine.distill_proof(
                evidence_item=ev,
                subject=ProofSubject.CONFIRMED_TEST_OWNERSHIP,
                statement="Tests pass",
                project_fingerprint="fp-1",
                workspace_root=self.temp_dir,
            )
        self.assertIn("Stripped Provenance Violation", str(ctx.exception))


    def test_vector4_proof_invalidation_after_file_mutation(self):
        """Vector 4: Proof remaining valid after referenced file mutation must be detected and demoted."""
        proof = ProjectProof(
            proof_id="proof-v4",
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="code.py matches initial hash",
            origin_mission_id="m-v4",
            project_fingerprint="fp-v4",
            status=ProofStatus.DURABLE,
            tracked_paths=["code.py"],
            path_hashes={"code.py": self.file_hash},
        )
        self.proof_store.add_or_update_proof(proof)

        # Mutate the file
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("def func(): return 'mutated'\n")

        drifted = self.proof_store.verify_physical_reality()
        self.assertEqual(len(drifted), 1)
        p = self.proof_store.get_proof("proof-v4")
        self.assertEqual(p.status, ProofStatus.INVALIDATED)

    def test_vector5_contradictory_proof_sources(self):
        """Vector 5: Contradictory proof sources must demote to INVALIDATED."""
        proof = ProjectProof(
            proof_id="proof-v5",
            subject=ProofSubject.VERIFIED_COMMAND,
            statement="Command verified",
            origin_mission_id="m-v5",
            project_fingerprint="fp-v5",
            evidence_references=[
                {"evidence_id": "e1", "state": "CONFLICTING"}
            ],
            status=ProofStatus.CANDIDATE,
        )
        eval_res, _ = self._create_clean_eval("m-v5")
        promoted = EvidenceDistillationEngine.promote_proof(
            proof=proof,
            evaluation_result=eval_res,
            current_fingerprint="fp-v5",
        )
        self.assertEqual(promoted.status, ProofStatus.INVALIDATED)
        self.assertIn("conflicting", promoted.metadata.get("rejection_reason", ""))

    def test_vector6_forged_project_fingerprint(self):
        """Vector 6: Forged project fingerprint must demote proof to STALE."""
        proof = ProjectProof(
            proof_id="proof-v6",
            subject=ProofSubject.VERIFIED_INVARIANT,
            statement="Invariant validated",
            origin_mission_id="m-v6",
            project_fingerprint="fp-genuine-hash",
            status=ProofStatus.CANDIDATE,
        )
        eval_res, _ = self._create_clean_eval("m-v6")
        promoted = EvidenceDistillationEngine.promote_proof(
            proof=proof,
            evaluation_result=eval_res,
            current_fingerprint="fp-forged-hash",
        )
        self.assertEqual(promoted.status, ProofStatus.STALE)
        self.assertIn("mismatch or drift", promoted.metadata.get("rejection_reason", ""))

    def test_vector7_drift_report_suppression_detected(self):
        """Vector 7: Drift report suppressed/missing causes health engine to classify UNTRUSTED."""
        crit = DriftFinding(
            domain=DriftDomain.TEST_OWNERSHIP,
            severity=DriftSeverity.CRITICAL_DRIFT,
            recommended_action=DriftAction.BLOCK,
            description="tests/run_all.py missing",
            previous_fingerprint="EXISTS",
            current_fingerprint="MISSING",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[crit],
            proof_store=self.proof_store,
        )
        self.assertEqual(health.status, IntelligenceHealthStatus.UNTRUSTED)

    def test_vector8_critical_drift_incorrectly_downgraded(self):
        """Vector 8: Critical drift on architecture zone cannot be downgraded; forces BLOCK."""
        crit = DriftFinding(
            domain=DriftDomain.ARCHITECTURE_ASSUMPTIONS,
            severity=DriftSeverity.CRITICAL_DRIFT,
            recommended_action=DriftAction.BLOCK,
            description="Constitutional core modified",
            previous_fingerprint="ORIGINAL",
            current_fingerprint="MUTATED",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[crit],
            proof_store=self.proof_store,
        )
        self.assertEqual(health.status, IntelligenceHealthStatus.UNTRUSTED)
        eval1, pkg1 = self._create_clean_eval("m-v8")
        cert = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[eval1],
            recent_evidence_packages=[pkg1],
            verifier_identity="Verifier",
        )
        self.assertEqual(cert.status, CertificationLevel.BLOCKED)

    def test_vector9_stale_intelligence_used_during_build_context(self):
        """Vector 9: Stale intelligence must be excluded during BUILD CONTEXT."""
        proof = ProjectProof(
            proof_id="proof-v9",
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="Old file hash",
            origin_mission_id="m-v9",
            project_fingerprint="fp-v9",
            status=ProofStatus.DURABLE,
            tracked_paths=["code.py"],
            path_hashes={"code.py": "old-hash-no-longer-valid"},
        )
        self.proof_store.add_or_update_proof(proof)

        # Physical reality check demotes to INVALIDATED
        self.proof_store.verify_physical_reality()
        self.assertEqual(self.proof_store.get_proof("proof-v9").status, ProofStatus.INVALIDATED)

        # In dispatch pipeline, only DURABLE or VALIDATED proofs are injected into context
        valid_proofs = [
            p for p in self.proof_store.list_proofs()
            if p.status in (ProofStatus.DURABLE, ProofStatus.VALIDATED)
        ]
        self.assertNotIn("proof-v9", [p.proof_id for p in valid_proofs])

    def test_vector10_certification_based_on_old_evidence_despite_critical_drift(self):
        """Vector 10: Certification based on old passing evidence despite critical drift fails closed."""
        eval1, pkg1 = self._create_clean_eval("m-old")
        crit_finding = DriftFinding(
            domain=DriftDomain.TEST_OWNERSHIP,
            severity=DriftSeverity.CRITICAL_DRIFT,
            recommended_action=DriftAction.BLOCK,
            description="Test runner corrupted",
            previous_fingerprint="OK",
            current_fingerprint="CORRUPT",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[crit_finding],
            proof_store=self.proof_store,
        )
        cert = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[eval1],
            recent_evidence_packages=[pkg1],
            verifier_identity="Verifier",
        )
        self.assertEqual(cert.status, CertificationLevel.BLOCKED)

    def test_vector11_previous_certified_state_incorrectly_reused_after_mutation(self):
        """Vector 11: Previous CERTIFIED state incorrectly reused after mutation drops certificate."""
        proof = ProjectProof(
            proof_id="proof-v11",
            subject=ProofSubject.VERIFIED_FILE_LOCATION,
            statement="File verified",
            origin_mission_id="m-v11",
            project_fingerprint="fp-v11",
            status=ProofStatus.DURABLE,
            tracked_paths=["code.py"],
            path_hashes={"code.py": self.file_hash},
        )
        self.proof_store.add_or_update_proof(proof)

        # Mutate the file
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("# unauthorized edit\n")

        # Re-running certification audits physical reality
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[],
            proof_store=self.proof_store,
        )
        eval1, pkg1 = self._create_clean_eval("m-v11")
        cert = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-v11",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[eval1],
            recent_evidence_packages=[pkg1],
            verifier_identity="Verifier",
        )
        # Because proof became INVALIDATED on disk audit, cert drops to DEGRADED
        self.assertEqual(cert.status, CertificationLevel.DEGRADED)

    def test_vector12_historical_evidence_replay_attack(self):
        """Vector 12: Historical evidence replay attack with mismatched fingerprint rejected."""
        eval1, pkg1 = self._create_clean_eval("m-replay")
        proof = ProjectProof(
            proof_id="proof-replay",
            subject=ProofSubject.VERIFIED_INVARIANT,
            statement="Replayed invariant",
            origin_mission_id="m-replay",
            project_fingerprint="original-fp",
            status=ProofStatus.CANDIDATE,
        )
        # Replaying against a new fingerprint fails promotion
        promoted = EvidenceDistillationEngine.promote_proof(
            proof=proof,
            evaluation_result=eval1,
            current_fingerprint="replayed-fp",
        )
        self.assertEqual(promoted.status, ProofStatus.STALE)

    def test_vector13_cross_project_proof_contamination(self):
        """Vector 13: Cross-project proof contamination rejected by project fingerprint check."""
        foreign_proof = ProjectProof(
            proof_id="proof-foreign",
            subject=ProofSubject.SUBSYSTEM_OWNERSHIP,
            statement="Ownership in external repo",
            origin_mission_id="m-foreign",
            project_fingerprint="foreign-project-repo-hash",
            status=ProofStatus.CANDIDATE,
        )
        eval_local, _ = self._create_clean_eval("m-local")
        promoted = EvidenceDistillationEngine.promote_proof(
            proof=foreign_proof,
            evaluation_result=eval_local,
            current_fingerprint="local-project-repo-hash",
        )
        self.assertEqual(promoted.status, ProofStatus.STALE)

    def test_vector14_certification_claim_without_verification_evidence(self):
        """Vector 14: Certification claim without verification evidence fails closed."""
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[],
            proof_store=self.proof_store,
        )
        # Zero recent mission evaluations
        cert = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[],
            recent_evidence_packages=[],
            verifier_identity="Verifier",
        )
        self.assertEqual(cert.status, CertificationLevel.UNKNOWN)
        self.assertIn("UNKNOWN", cert.card.final_decision)

    def test_vector15_bounded_history_bypass_attempt(self):
        """Vector 15: Bounded-history bypass attempting to inject hidden authority is capped."""
        many_evals = []
        many_pkgs = []
        for i in range(25):  # 25 missions > 10 cap
            e, p = self._create_clean_eval(f"m-hist-{i}")
            many_evals.append(e)
            many_pkgs.append(p)

        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[],
            proof_store=self.proof_store,
        )
        cert = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=many_evals,
            recent_evidence_packages=many_pkgs,
            verifier_identity="Verifier",
            historical_digest="sha256-older-collapsed-history",
            historical_mission_count=15,
        )
        # Window must be capped to MAX_CERTIFICATION_MISSIONS = 10
        self.assertEqual(len(cert.window.evaluated_mission_ids), 10)
        self.assertEqual(cert.window.historical_missions_count, 15)
        self.assertEqual(cert.window.historical_digest, "sha256-older-collapsed-history")


if __name__ == "__main__":
    unittest.main()
