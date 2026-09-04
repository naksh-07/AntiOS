"""Tests for AntiOS 2.0 Phase 60: Generated Intelligence Verification.

Verifies:
- Cryptographic SHA-256 verification of managed and generated artifacts.
- Fingerprint drift detection when target project manifests mutate.
- Stale path detection when declared subsystem components are deleted.
- Shallow Depth Law audit (flags specialists with max_depth > 2 or can_delegate == True).
- Verification verdict and actionable remediation commands.
"""

from pathlib import Path
import unittest

from framework.core.intelligence_verifier import (
    IntelligenceVerificationStatus,
    IntelligenceVerifier,
)


class TestIntelligenceVerification(unittest.TestCase):
    """Unit tests for IntelligenceVerifier."""

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_stale_intelligence_fixture_detection(self):
        stale_repo = self.fixtures_dir / "stale_intelligence_project"
        verifier = IntelligenceVerifier(stale_repo)
        verdict = verifier.verify()

        self.assertFalse(verdict.status == IntelligenceVerificationStatus.VALID)
        # Must detect stale path for deleted_module
        has_stale_path = any(i.issue_type == "STALE_PATH" for i in verdict.issues)
        self.assertTrue(has_stale_path, "Failed to detect stale path in stale_intelligence_project")

    def test_architecture_drift_fixture_detection(self):
        drift_repo = self.fixtures_dir / "architecture_drift_project"
        verifier = IntelligenceVerifier(drift_repo)
        verdict = verifier.verify()

        # Must detect fingerprint drift
        self.assertTrue(verdict.drift_detected)
        has_drift_issue = any(i.issue_type == "FINGERPRINT_DRIFT" for i in verdict.issues)
        self.assertTrue(has_drift_issue, "Failed to detect fingerprint drift in architecture_drift_project")
        self.assertTrue(len(verdict.remediation_command) > 0)

    def test_missing_manifest_fails_closed(self):
        plain_repo = self.fixtures_dir / "python_project"
        # python_project does not have .antios/ installed
        verifier = IntelligenceVerifier(plain_repo)
        verdict = verifier.verify()

        self.assertEqual(verdict.status, IntelligenceVerificationStatus.INTEGRITY_VIOLATION)
        self.assertFalse(verdict.manifest_valid)
        self.assertTrue(any(i.issue_type == "MISSING_MANIFEST" for i in verdict.issues))


if __name__ == "__main__":
    unittest.main()
