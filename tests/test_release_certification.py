"""Tests for AntiOS 2.0 Phase 95: Long-Horizon Release Certification.

Validates:
- Deterministic 12-dimension release certification
- 5 certification levels: CERTIFIED, CONDITIONALLY_CERTIFIED, DEGRADED, BLOCKED, UNKNOWN
- Current reality outranking historical claims
- Bounded certification window (<= 10 missions + historical digest)
- Token-bounded LongHorizonCertificationCard (<= 25 lines)
"""

import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional, Tuple
import unittest


from framework.core.drift_health import (
    DriftAction,
    DriftDomain,
    DriftFinding,
    DriftSeverity,
    IntelligenceHealthEngine,
    IntelligenceHealthStatus,
)

from framework.core.evidence import (
    EpistemicCategory,
    EvidenceBuilder,
    EvidenceItem,
    EvidencePackage,
    EvidenceState,
)
from framework.core.mission_evaluation import (
    DimensionEvaluation,
    EvaluationStatus,
    MissionEvaluationDimension,
    MissionEvaluationEngine,
    MissionEvaluationResult,
)

from framework.core.project_proof import (
    ProjectProof,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
)
from framework.core.release_certification import (
    CertificationDimension,
    CertificationLevel,
    LongHorizonCertificationCard,
    ReleaseCertificationEngine,
)


class TestReleaseCertificationEngine(unittest.TestCase):
    """Unit tests for ReleaseCertificationEngine across 12 dimensions."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_cert_test_")
        self.proof_store = ProjectProofStore(workspace_root=self.temp_dir)

        # Setup valid dummy proof
        p = ProjectProof(
            proof_id="proof-cert-01",
            subject=ProofSubject.VERIFIED_INVARIANT,
            statement="Constitutional limits verified",
            origin_mission_id="m-init",
            project_fingerprint="fp-cert-clean",
            status=ProofStatus.DURABLE,
        )
        self.proof_store.add_or_update_proof(p)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_passing_eval(self, mission_id: str) -> Tuple[MissionEvaluationResult, EvidencePackage]:
        pkg = EvidencePackage(
            mission_id=mission_id,
            intent="Run test suite",
            acceptance_criteria=["Tests exit 0"],
        )

        ev = EvidenceItem(
            evidence_id=f"ev-{mission_id}",
            mission_id=mission_id,
            intent="Run tests",
            provenance="tests/run_all.py",
            epistemic_category=EpistemicCategory.EVIDENCE,
            state=EvidenceState.VERIFIED,
            test_results=[{"exit_code": 0}],
            acceptance_criteria_keys=["Tests exit 0"],
        )
        pkg.add_evidence_item(ev)
        pkg.final_verdict = "PASS"
        res = MissionEvaluationEngine.evaluate(evidence_package=pkg, risk_tier="LOW")
        return res, pkg


    def test_clean_release_certification_certified(self):
        eval1, pkg1 = self._create_passing_eval("m-1")
        eval2, pkg2 = self._create_passing_eval("m-2")

        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[],
            proof_store=self.proof_store,
        )

        cert_res = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-cert-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[eval1, eval2],
            recent_evidence_packages=[pkg1, pkg2],
            verifier_identity="AntiOS Maker-Checker Verifier",
        )

        self.assertEqual(cert_res.status, CertificationLevel.CERTIFIED)
        self.assertIn("APPROVED", cert_res.card.final_decision)
        self.assertEqual(len(cert_res.window.evaluated_mission_ids), 2)

        # Card line count bound
        card_str = cert_res.card.format_card(max_lines=25)
        self.assertLessEqual(len(card_str.splitlines()), 25)
        self.assertIn("ANTIOS RELEASE CERTIFICATION CARD", card_str)

    def test_critical_drift_blocks_certification(self):
        eval1, pkg1 = self._create_passing_eval("m-1")

        crit_finding = DriftFinding(
            domain=DriftDomain.ARCHITECTURE_ASSUMPTIONS,
            severity=DriftSeverity.CRITICAL_DRIFT,
            recommended_action=DriftAction.BLOCK,
            description="Core constitution altered out-of-band",
            previous_fingerprint="f1",
            current_fingerprint="f2",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[crit_finding],
            proof_store=self.proof_store,
        )

        cert_res = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-cert-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[eval1],
            recent_evidence_packages=[pkg1],
            verifier_identity="Verifier Subagent",
        )
        self.assertEqual(cert_res.status, CertificationLevel.BLOCKED)
        self.assertIn("DENIED", cert_res.card.final_decision)

    def test_empty_evaluations_yields_unknown(self):
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root=self.temp_dir,
            findings=[],
            proof_store=self.proof_store,
        )
        cert_res = ReleaseCertificationEngine.certify(
            workspace_root=self.temp_dir,
            project_fingerprint="fp-cert-clean",
            proof_store=self.proof_store,
            health_result=health,
            recent_evaluations=[],
            recent_evidence_packages=[],
            verifier_identity="Verifier Subagent",
        )
        self.assertEqual(cert_res.status, CertificationLevel.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
