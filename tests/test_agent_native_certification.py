"""Tests for Phase 78 Agent-Native Certification Engine."""

from pathlib import Path
import tempfile
import unittest

from framework.core.agent_native_certification import (
    AgentNativeCertification,
    AgentNativeCertificationEngine,
    CertificationLevel,
)


class TestAgentNativeCertification(unittest.TestCase):
    """Test suite for AgentNativeCertificationEngine."""

    def test_certify_current_repository_passes(self):
        """Current repository passes certification as AGENT_READY or HIGHLY_AGENT_NATIVE."""
        cert = AgentNativeCertificationEngine.certify(".")
        self.assertIsInstance(cert, AgentNativeCertification)
        self.assertTrue(cert.is_certified)
        self.assertIn(
            cert.certification_level,
            [CertificationLevel.AGENT_READY, CertificationLevel.HIGHLY_AGENT_NATIVE, CertificationLevel.CERTIFIED],
        )
        self.assertEqual(len(cert.critical_findings), 0)

    def test_fail_closed_on_legacy_workflows(self):
        """Presence of .agents/workflows/ immediately fails closed with NOT_READY."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wf = Path(tmpdir) / ".agents" / "workflows"
            wf.mkdir(parents=True)
            (wf / "old_wf.md").write_text("workflow", encoding="utf-8")

            cert = AgentNativeCertificationEngine.certify(tmpdir)
            self.assertEqual(cert.certification_level, CertificationLevel.NOT_READY)
            self.assertFalse(cert.is_certified)
            self.assertTrue(
                any("workflows" in cf.lower() for cf in cert.critical_findings),
                "Expected legacy workflows in critical findings.",
            )

    def test_fail_closed_on_specialist_delegation_violation(self):
        """Specialist declaring can_delegate: true fails closed with NOT_READY."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / ".agents" / "skills" / "illegal_delegator"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: illegal_delegator\ncan_delegate: true\n---\nPrompt", encoding="utf-8"
            )

            cert = AgentNativeCertificationEngine.certify(tmpdir)
            self.assertEqual(cert.certification_level, CertificationLevel.NOT_READY)
            self.assertFalse(cert.is_certified)
            self.assertTrue(
                any("shallow depth" in cf.lower() or "can_delegate" in cf.lower() for cf in cert.critical_findings)
            )

    def test_formal_report_structure(self):
        """Formal report formatting matches required structure."""
        cert = AgentNativeCertificationEngine.certify(".")
        report = cert.to_formal_report()
        self.assertIn("AGENT_NATIVE_CERTIFICATION", report)
        self.assertIn("Project:", report)
        self.assertIn("Fingerprint:", report)
        self.assertIn("Overall Score:", report)
        self.assertIn("Dimension Scores:", report)


if __name__ == "__main__":
    unittest.main()
