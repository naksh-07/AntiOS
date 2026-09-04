"""Unit tests for AntiOS 2.0 Artifact Ownership & Provenance Engine."""

from pathlib import Path
import tempfile
import unittest

from framework.core.manifest import (
    ArtifactOwnership,
    ArtifactRecord,
    ProjectManifest,
    save_manifest,
)
from framework.core.provenance import (
    ProvenanceTracker,
    can_safely_overwrite,
    classify_artifact,
    compute_file_sha256,
)


class TestProvenanceOwnership(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.target_root = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_classify_artifact_ownership(self):
        manifest = ProjectManifest(
            project_fingerprint="fp1",
            source_revision="v2.0.0",
            protected_paths=["protected_dir", "antios.config.json"],
            user_owned_paths=["user_script.py"],
            managed_paths={
                "managed.json": ArtifactRecord(
                    path="managed.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256="hash_managed",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            generated_paths={
                "generated.json": ArtifactRecord(
                    path="generated.json",
                    ownership=ArtifactOwnership.GENERATED,
                    sha256="hash_gen",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
        )

        # 1. AntiOS Immutable
        owner, _ = classify_artifact("framework/core/guard.py", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.ANTIOS_IMMUTABLE)

        # 2. Project Protected
        owner, _ = classify_artifact("protected_dir/file.ts", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.PROJECT_PROTECTED)

        # 3. Explicit User Authored
        owner, _ = classify_artifact("user_script.py", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.USER_AUTHORED)

        # 4. Managed
        owner, _ = classify_artifact("managed.json", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.MANAGED)

        # 5. Generated
        owner, _ = classify_artifact("generated.json", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.GENERATED)

        # 6. Pre-existing untracked file
        untracked = self.target_root / "untracked.py"
        untracked.write_text("print('hello')", encoding="utf-8")
        owner, _ = classify_artifact("untracked.py", manifest, self.target_root)
        self.assertEqual(owner, ArtifactOwnership.USER_AUTHORED)

    def test_can_safely_overwrite_blocks_user_modified_files(self):
        managed_file = self.target_root / "managed.json"
        managed_file.write_text('{"initial": true}', encoding="utf-8")
        initial_sha = compute_file_sha256(managed_file)

        manifest = ProjectManifest(
            project_fingerprint="fp1",
            source_revision="v2.0.0",
            managed_paths={
                "managed.json": ArtifactRecord(
                    path="managed.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256=initial_sha,
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
        )

        # Before modification: safe to overwrite/update
        can_ow, reason = can_safely_overwrite("managed.json", manifest, self.target_root)
        self.assertTrue(can_ow)

        # User modifies the file
        managed_file.write_text('{"user_edited": true}', encoding="utf-8")

        # After modification: strictly blocked!
        can_ow, reason = can_safely_overwrite("managed.json", manifest, self.target_root)
        self.assertFalse(can_ow)
        self.assertIn("modified by the user", reason)

    def test_can_safely_overwrite_blocks_untracked_and_protected_files(self):
        manifest = ProjectManifest(
            project_fingerprint="fp1",
            source_revision="v2.0.0",
            protected_paths=["core/domain"],
        )

        # 1. Untracked existing file -> blocked
        untracked = self.target_root / "app.py"
        untracked.write_text("code", encoding="utf-8")
        can_ow, reason = can_safely_overwrite("app.py", manifest, self.target_root)
        self.assertFalse(can_ow)
        self.assertIn("UNKNOWN ownership", reason)

        # 2. File in protected path -> blocked
        can_ow, reason = can_safely_overwrite("core/domain/engine.py", manifest, self.target_root)
        self.assertFalse(can_ow)
        self.assertIn("protected project", reason.lower())

    def test_provenance_tracker_audits_conflicts(self):
        # Create a managed file and modify it
        managed_path = self.target_root / "config.json"
        managed_path.write_text('{"original": 1}', encoding="utf-8")
        orig_sha = compute_file_sha256(managed_path)
        managed_path.write_text('{"user_mod": 2}', encoding="utf-8")

        manifest = ProjectManifest(
            project_fingerprint="fp1",
            source_revision="v2.0.0",
            managed_paths={
                "config.json": ArtifactRecord(
                    path="config.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256=orig_sha,
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            generated_paths={
                "missing.json": ArtifactRecord(
                    path="missing.json",
                    ownership=ArtifactOwnership.GENERATED,
                    sha256="missing_hash",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            stale_paths=["stale.tmp"],
        )

        (self.target_root / "stale.tmp").write_text("old", encoding="utf-8")

        tracker = ProvenanceTracker(self.target_root, manifest)
        conflicts = tracker.audit_artifacts()

        conflict_types = {c.conflict_type for c in conflicts}
        self.assertIn("USER_MODIFIED", conflict_types)
        self.assertIn("MISSING_GENERATED", conflict_types)
        self.assertIn("STALE_REMNANT", conflict_types)


if __name__ == "__main__":
    unittest.main()
