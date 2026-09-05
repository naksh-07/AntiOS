"""Tests for AntiOS 2.0 Phase 94: Runtime Drift Detection & Intelligence Health.

Validates:
- Event-driven drift detection across canonical domains
- Severity classification (NO_DRIFT, MINOR_DRIFT, SIGNIFICANT_DRIFT, CRITICAL_DRIFT)
- Governance actions (NONE, REFRESH, REVERIFY, REPLAN, REBUILD_INTELLIGENCE, BLOCK)
- 7 defensible intelligence health dimensions
- Proposal-governed repair engine without autonomous architecture mutation
- Token-bounded DriftHealthCard (<= 25 lines)
"""

import hashlib
import os
import shutil
import tempfile
import unittest

from framework.core.drift_health import (
    DriftAction,
    DriftDomain,
    DriftFinding,
    DriftHealthCard,
    DriftSeverity,
    IntelligenceHealthEngine,
    IntelligenceHealthResult,
    IntelligenceHealthStatus,
    IntelligenceRepairEngine,
    ProjectDriftEngine,
    RepairActionType,
)
from framework.core.project_proof import (
    ProjectProof,
    ProjectProofStore,
    ProofStatus,
    ProofSubject,
)


class TestRuntimeDriftEngine(unittest.TestCase):
    """Unit tests for ProjectDriftEngine detecting on-disk drift."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="antios_drift_test_")
        # Setup clean dummy files
        self.manifest = os.path.join(self.temp_dir, "antios.config.json")
        with open(self.manifest, "w", encoding="utf-8") as f:
            f.write('{"version": "2.0"}')
        with open(self.manifest, "rb") as f:
            self.manifest_hash = hashlib.sha256(f.read()).hexdigest()

        # Dummy test runner
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        self.runner = os.path.join(self.temp_dir, "tests", "run_all.py")
        with open(self.runner, "w", encoding="utf-8") as f:
            f.write("# runner\n")

        # Dummy constitution
        self.const_file = os.path.join(self.temp_dir, "ANTIOS_CONSTITUTION.md")
        with open(self.const_file, "w", encoding="utf-8") as f:
            f.write("# Constitution\n")
        with open(self.const_file, "rb") as f:
            self.const_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_clean_state_detects_no_drift(self):
        recorded = {
            "manifest_hash": self.manifest_hash,
            "core_ANTIOS_CONSTITUTION.md": self.const_hash,
        }
        findings = ProjectDriftEngine.evaluate_drift(
            workspace_root=self.temp_dir,
            manifest_path=self.manifest,
            recorded_fingerprints=recorded,
        )
        self.assertEqual(len(findings), 0)

    def test_manifest_drift_detected(self):
        recorded = {
            "manifest_hash": "different-old-hash",
            "core_ANTIOS_CONSTITUTION.md": self.const_hash,
        }
        findings = ProjectDriftEngine.evaluate_drift(
            workspace_root=self.temp_dir,
            manifest_path=self.manifest,
            recorded_fingerprints=recorded,
        )
        manifest_findings = [f for f in findings if f.domain == DriftDomain.PROJECT_MANIFEST]
        self.assertEqual(len(manifest_findings), 1)
        self.assertEqual(manifest_findings[0].severity, DriftSeverity.SIGNIFICANT_DRIFT)
        self.assertEqual(manifest_findings[0].recommended_action, DriftAction.REFRESH)

    def test_critical_architecture_tampering_triggers_block(self):
        recorded = {
            "manifest_hash": self.manifest_hash,
            "core_ANTIOS_CONSTITUTION.md": "original-hash-1234",
        }
        findings = ProjectDriftEngine.evaluate_drift(
            workspace_root=self.temp_dir,
            manifest_path=self.manifest,
            recorded_fingerprints=recorded,
        )
        crit_findings = [f for f in findings if f.domain == DriftDomain.ARCHITECTURE_ASSUMPTIONS]
        self.assertEqual(len(crit_findings), 1)
        self.assertEqual(crit_findings[0].severity, DriftSeverity.CRITICAL_DRIFT)
        self.assertEqual(crit_findings[0].recommended_action, DriftAction.BLOCK)

    def test_active_context_budget_drift(self):
        os.makedirs(os.path.join(self.temp_dir, "docs"), exist_ok=True)
        ac_file = os.path.join(self.temp_dir, "docs", "ACTIVE_CONTEXT.md")
        with open(ac_file, "w", encoding="utf-8") as f:
            for i in range(75):  # 75 lines > 60 budget limit
                f.write(f"Line {i}\n")

        recorded = {
            "manifest_hash": self.manifest_hash,
            "core_ANTIOS_CONSTITUTION.md": self.const_hash,
        }
        findings = ProjectDriftEngine.evaluate_drift(
            workspace_root=self.temp_dir,
            manifest_path=self.manifest,
            recorded_fingerprints=recorded,
        )
        doc_findings = [f for f in findings if f.domain == DriftDomain.DOCUMENTATION]
        self.assertEqual(len(doc_findings), 1)
        self.assertEqual(doc_findings[0].severity, DriftSeverity.MINOR_DRIFT)


class TestIntelligenceHealthAndRepair(unittest.TestCase):
    """Unit tests for 7-dimension health assessment and repair proposals."""

    def test_healthy_evaluation(self):
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root="dummy",
            findings=[],
        )
        self.assertEqual(health.status, IntelligenceHealthStatus.HEALTHY)
        self.assertEqual(health.dimension_scores["test_mapping_integrity"], 1.0)
        self.assertEqual(health.dimension_scores["adapter_integrity"], 1.0)
        self.assertEqual(len(health.proposals), 0)

    def test_untrusted_on_critical_drift(self):
        crit_finding = DriftFinding(
            domain=DriftDomain.ARCHITECTURE_ASSUMPTIONS,
            severity=DriftSeverity.CRITICAL_DRIFT,
            recommended_action=DriftAction.BLOCK,
            description="Constitution modified without governance",
            previous_fingerprint="old",
            current_fingerprint="new",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root="dummy",
            findings=[crit_finding],
        )
        self.assertEqual(health.status, IntelligenceHealthStatus.UNTRUSTED)
        self.assertEqual(len(health.proposals), 1)
        self.assertEqual(health.proposals[0].action_type, RepairActionType.REQUEST_HUMAN_REVIEW)

    def test_drift_health_card_formatting(self):
        finding = DriftFinding(
            domain=DriftDomain.PROJECT_MANIFEST,
            severity=DriftSeverity.SIGNIFICANT_DRIFT,
            recommended_action=DriftAction.REFRESH,
            description="Manifest config drifted",
            previous_fingerprint="f1",
            current_fingerprint="f2",
        )
        health = IntelligenceHealthEngine.evaluate_health(
            workspace_root="dummy",
            findings=[finding],
        )
        card = IntelligenceRepairEngine.emit_summary_card(health)
        formatted = card.format_card(max_lines=25)
        self.assertLessEqual(len(formatted.splitlines()), 25)
        self.assertIn("ANTIOS INTELLIGENCE HEALTH CARD", formatted)


if __name__ == "__main__":
    unittest.main()
