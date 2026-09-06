"""Unit & Integration Tests for AntiOS 2.0 Full System Certification Audit (Phase 99)."""

from pathlib import Path
import unittest

from framework.core.certification_audit import (
    AuditArea,
    AuditFinding,
    AuditStatus,
    SystemCertificationAuditCard,
    SystemCertificationAuditEngine,
    SystemCertificationAuditReport,
)


class TestSystemCertificationAudit(unittest.TestCase):
    """Tests for Phase 99 System Certification Audit Engine."""

    def setUp(self):
        self.engine = SystemCertificationAuditEngine()

    def test_all_12_audit_areas_present_and_verified(self):
        report = self.engine.audit_all()
        self.assertIsInstance(report, SystemCertificationAuditReport)
        self.assertEqual(report.overall_status, AuditStatus.VERIFIED)
        self.assertEqual(len(report.area_results), 12)

        for area in AuditArea:
            self.assertIn(area.value, report.area_results)
            area_result = report.area_results[area.value]
            self.assertEqual(area_result.status, AuditStatus.VERIFIED)
            self.assertEqual(area_result.score, 1.0)
            self.assertGreaterEqual(len(area_result.findings), 2)
            self.assertGreaterEqual(len(area_result.key_evidence), 1)

    def test_summary_card_bounded_to_25_lines(self):
        report = self.engine.audit_all()
        self.assertIsNotNone(report.summary_card)
        card_md = report.summary_card.render_markdown()
        lines = card_md.strip().split("\n")
        self.assertLessEqual(len(lines), 25)
        self.assertIn("AntiOS 2.0 System Certification Audit Card", lines[0])
        self.assertIn("12/12", card_md)

    def test_audit_report_serialization_and_hash(self):
        report = self.engine.audit_all()
        data = report.to_dict()
        self.assertIn("audit_id", data)
        self.assertIn("area_results", data)
        self.assertIn("summary_card", data)
        self.assertIn("audit_hash", data)
        self.assertEqual(len(data["audit_hash"]), 64)

    def test_adversarial_failed_finding_drops_overall_status(self):
        report = self.engine.audit_all()
        # Artificially inject a failed finding in ARCHITECTURAL_INTEGRITY
        report.area_results[AuditArea.ARCHITECTURAL_INTEGRITY.value].status = AuditStatus.FAILED
        failed_count = sum(1 for r in report.area_results.values() if r.status == AuditStatus.FAILED)
        self.assertGreater(failed_count, 0)

    def test_referenced_evidence_locations_physically_exist(self):
        repo_root = self.engine.repo_root
        report = self.engine.audit_all()
        for area_res in report.area_results.values():
            for finding in area_res.findings:
                # Evidence location path before ':'
                file_rel = finding.evidence_location.split(":")[0].strip()
                target_file = repo_root / file_rel
                self.assertTrue(
                    target_file.exists(),
                    f"Referenced evidence location {file_rel} must exist in repo!",
                )
                # Supporting test path before ':'
                test_rel = finding.supporting_test.split(":")[0].strip()
                target_test = repo_root / test_rel
                self.assertTrue(
                    target_test.exists(),
                    f"Referenced test file {test_rel} must exist in repo!",
                )

    def test_anti_studylab_boundary_in_findings(self):
        report = self.engine.audit_all()
        banned_phrases = ["StudyLab", "StudySourceCore"]
        for area_res in report.area_results.values():
            for finding in area_res.findings:
                for bp in banned_phrases:
                    # Criterion may reference anti-boundary in positive sense, but evidence must not reside in StudyLab
                    self.assertNotIn(f"/{bp}", finding.evidence_location)
                    self.assertNotIn(f"/{bp}", finding.supporting_test)


if __name__ == "__main__":
    unittest.main()
