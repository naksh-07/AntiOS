"""Tests for Phase 90: Evidence Architecture.

Verifies:
1. Epistemic Category segregation (OBSERVATION != EVIDENCE != VERDICT != INFERENCE != DECISION).
2. The 6 canonical evidence lifecycle states.
3. Strict rejection of unbacked agent assertions posing as physical EVIDENCE.
4. Artifact fingerprinting with before/after SHA-256.
5. Deterministic, bounded EvidencePackage container limits.
6. Evidence persistence and roundtrip JSON serialization.
7. ToolOutputClassifier bounding on large command execution.
8. EvidenceBuilder fluent package generation.
9. Enforced non-empty provenance requirement.
"""

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


class TestEvidenceArchitecture(unittest.TestCase):
    """Test suite for Phase 90 Evidence Architecture."""

    def test_epistemic_category_segregation(self):
        """Rule: OBSERVATION, EVIDENCE, VERDICT, INFERENCE, and DECISION are distinct."""
        self.assertNotEqual(EpistemicCategory.OBSERVATION, EpistemicCategory.EVIDENCE)
        self.assertNotEqual(EpistemicCategory.EVIDENCE, EpistemicCategory.VERDICT)
        self.assertNotEqual(EpistemicCategory.VERDICT, EpistemicCategory.INFERENCE)
        self.assertNotEqual(EpistemicCategory.INFERENCE, EpistemicCategory.DECISION)
        self.assertEqual(len(EpistemicCategory), 5)

    def test_six_canonical_evidence_states(self):
        """Rule: The 6 canonical lifecycle states are well-defined."""
        states = {s.value for s in EvidenceState}
        self.assertEqual(
            states,
            {"OBSERVED", "VERIFIED", "INVALIDATED", "SUPERSEDED", "MISSING", "CONFLICTING"},
        )

    def test_agent_assertion_cannot_pose_as_unbacked_evidence(self):
        """Rule: An agent claim cannot be created as EVIDENCE without physical verification."""
        with self.assertRaises(ValueError) as ctx:
            EvidenceItem(
                evidence_id="ev-1",
                mission_id="m-1",
                intent="Fix bug",
                provenance="Worker statement",
                epistemic_category=EpistemicCategory.EVIDENCE,
                worker_identity="agent-implementer-1",
                # No commands_executed, test_results, verification_verdicts, or invariant_checks
            )
        self.assertIn("Epistemic Separation Violation", str(ctx.exception))

    def test_agent_assertion_valid_as_inference_or_observation(self):
        """Rule: Agent claims may be registered as INFERENCE or OBSERVATION."""
        item = EvidenceItem(
            evidence_id="ev-inf-1",
            mission_id="m-1",
            intent="Hypothesis about timing bug",
            provenance="Worker reasoning trace",
            epistemic_category=EpistemicCategory.INFERENCE,
            worker_identity="agent-implementer-1",
        )
        self.assertEqual(item.epistemic_category, EpistemicCategory.INFERENCE)

    def test_provenance_is_mandatory(self):
        """Rule: Evidence items MUST have non-empty provenance."""
        with self.assertRaises(ValueError) as ctx:
            EvidenceItem(
                evidence_id="ev-no-prov",
                mission_id="m-1",
                intent="Verify build",
                provenance="",  # Empty!
                commands_executed=["pytest"],
                command_exit_codes={"pytest": 0},
            )
        self.assertIn("provenance is required", str(ctx.exception))

    def test_artifact_fingerprint_modification_detection(self):
        """Rule: ArtifactFingerprint tracks before/after SHA-256 and modification."""
        fp_unmodified = ArtifactFingerprint(
            path="core/utils.py",
            sha256_before="aaa",
            sha256_after="aaa",
        )
        self.assertFalse(fp_unmodified.is_modified())

        fp_modified = ArtifactFingerprint(
            path="core/utils.py",
            sha256_before="aaa",
            sha256_after="bbb",
        )
        self.assertTrue(fp_modified.is_modified())

        fp_created = ArtifactFingerprint(
            path="core/new.py",
            sha256_before="",
            sha256_after="ccc",
        )
        self.assertTrue(fp_created.is_modified())

    def test_evidence_package_bounds_enforcement(self):
        """Rule: EvidencePackage enforces caps on artifacts (<=50) and items (<=100)."""
        pkg = EvidencePackage(
            mission_id="m-large",
            intent="Large batch mission",
            acceptance_criteria=["Criterion 1"],
        )

        for i in range(70):
            fp = ArtifactFingerprint(path=f"file_{i}.py", sha256_after=f"sha_{i}")
            pkg.add_artifact(fp)
        self.assertEqual(len(pkg.changed_artifacts), 50)

        for i in range(120):
            item = EvidenceItem(
                evidence_id=f"item-{i}",
                mission_id="m-large",
                intent=f"Step {i}",
                provenance=f"runner-{i}",
                commands_executed=["test"],
                command_exit_codes={"test": 0},
            )
            pkg.add_evidence_item(item)
        self.assertEqual(len(pkg.evidence_items), 100)

    def test_package_roundtrip_persistence(self):
        """Rule: EvidencePackage saves to JSON and restores deterministically."""
        builder = EvidenceBuilder(
            mission_id="m-persist",
            intent="Test persistence",
            acceptance_criteria=["Must serialize and deserialize"],
        )
        builder.track_file_change("sample.py", "content before", "content after")
        builder.add_command_evidence("python -m unittest", 0, "Ran 1 test in 0.01s\n\nOK")
        pkg = builder.build(final_verdict="PASS")

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "evidence.json")
            pkg.save(file_path)
            self.assertTrue(os.path.exists(file_path))

            restored = EvidencePackage.load(file_path)
            self.assertEqual(restored.mission_id, "m-persist")
            self.assertEqual(restored.final_verdict, "PASS")
            self.assertEqual(len(restored.changed_artifacts), 1)
            self.assertEqual(len(restored.evidence_items), 1)
            self.assertEqual(restored.compute_evidence_hash(), pkg.compute_evidence_hash())

    def test_large_command_output_bounded_with_sha256(self):
        """Rule: Outputs >2000 chars are compacted with SHA-256."""
        pkg = EvidencePackage(
            mission_id="m-large-out",
            intent="Run verbose command",
            acceptance_criteria=["Output bounded"],
        )
        large_output = "Line of debug output\n" * 200  # > 4,000 chars
        ev = pkg.record_command("pytest -vv", 0, large_output)
        self.assertEqual(ev.classification.value, "SUMMARIZED")
        self.assertIn("truncated", ev.compact_summary)
        self.assertEqual(len(ev.raw_sha256), 64)


if __name__ == "__main__":
    unittest.main()
