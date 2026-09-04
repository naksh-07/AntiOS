"""Unit tests for AntiOS 2.0 Project Manifest Engine."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.manifest import (
    AdaptationState,
    ArtifactOwnership,
    ArtifactRecord,
    CURRENT_ANTIOS_VERSION,
    CURRENT_SCHEMA_VERSION,
    InstallationState,
    ProjectManifest,
    load_manifest,
    save_manifest,
)


class TestProjectManifest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.target_root = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_manifest_construction_and_validation(self):
        manifest = ProjectManifest(
            antios_version=CURRENT_ANTIOS_VERSION,
            schema_version=CURRENT_SCHEMA_VERSION,
            project_fingerprint="abc123def456",
            source_revision="v2.0.0",
            adaptation_state=AdaptationState.ADAPTED,
            installation_state=InstallationState.INSTALLED,
            managed_paths={
                "antios.config.json": ArtifactRecord(
                    path="antios.config.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256="hash1",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            generated_paths={
                ".antios/knowledge.json": ArtifactRecord(
                    path=".antios/knowledge.json",
                    ownership=ArtifactOwnership.GENERATED,
                    sha256="hash2",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
        )
        is_valid, issues = manifest.validate()
        self.assertTrue(is_valid, f"Validation issues: {issues}")
        self.assertEqual(len(issues), 0)

    def test_manifest_validation_fails_on_missing_required_fields(self):
        manifest = ProjectManifest(
            antios_version="",
            schema_version="",
            project_fingerprint="",
            source_revision="",
        )
        is_valid, issues = manifest.validate()
        self.assertFalse(is_valid)
        self.assertIn("Manifest missing valid 'antios_version'", issues)
        self.assertIn("Manifest missing valid 'project_fingerprint'", issues)

    def test_manifest_roundtrip_serialization(self):
        manifest = ProjectManifest(
            antios_version=CURRENT_ANTIOS_VERSION,
            schema_version=CURRENT_SCHEMA_VERSION,
            project_fingerprint="fingerprint_xyz",
            source_revision="v2.0.0",
            adaptation_state=AdaptationState.ADAPTED,
            installation_state=InstallationState.INSTALLED,
            managed_paths={
                "antios.config.json": ArtifactRecord(
                    path="antios.config.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256="sha_managed",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            user_owned_paths=[".agents/skills/custom/SKILL.md"],
            stale_paths=[".antios/old_cache.json"],
        )

        saved_path = save_manifest(manifest, self.target_root)
        self.assertTrue(saved_path.is_file())

        loaded = load_manifest(self.target_root)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.antios_version, CURRENT_ANTIOS_VERSION)
        self.assertEqual(loaded.project_fingerprint, "fingerprint_xyz")
        self.assertEqual(loaded.installation_state, InstallationState.INSTALLED)
        self.assertEqual(len(loaded.managed_paths), 1)
        self.assertEqual(loaded.managed_paths["antios.config.json"].sha256, "sha_managed")
        self.assertEqual(loaded.user_owned_paths, [".agents/skills/custom/SKILL.md"])
        self.assertEqual(loaded.stale_paths, [".antios/old_cache.json"])

    def test_load_manifest_fails_closed_on_corrupt_json(self):
        manifest_file = self.target_root / ".antios/manifest.json"
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text("{corrupt: json content", encoding="utf-8")

        with self.assertRaises(ValueError) as ctx:
            load_manifest(self.target_root)
        self.assertIn("Corrupted or invalid AntiOS manifest", str(ctx.exception))

    def test_manifest_query_helpers(self):
        manifest = ProjectManifest(
            project_fingerprint="test",
            source_revision="v2.0.0",
            managed_paths={
                "antios.config.json": ArtifactRecord(
                    path="antios.config.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256="sha1",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                    is_user_modified=False,
                ),
                "modified.json": ArtifactRecord(
                    path="modified.json",
                    ownership=ArtifactOwnership.MANAGED,
                    sha256="sha2",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                    is_user_modified=True,
                ),
            },
            generated_paths={
                ".antios/knowledge.json": ArtifactRecord(
                    path=".antios/knowledge.json",
                    ownership=ArtifactOwnership.GENERATED,
                    sha256="sha3",
                    source_revision="v2.0.0",
                    generated_at="2026-09-05T00:00:00Z",
                )
            },
            user_owned_paths=["src/custom.py"],
            stale_paths=[".antios/stale.json"],
        )

        self.assertTrue(manifest.is_artifact_owned_by_antios("antios.config.json"))
        self.assertTrue(manifest.is_artifact_owned_by_antios(".antios/knowledge.json"))
        self.assertFalse(manifest.is_artifact_owned_by_antios("src/custom.py"))

        self.assertTrue(manifest.is_artifact_user_owned("src/custom.py"))
        self.assertTrue(manifest.is_artifact_user_owned("modified.json"))
        self.assertFalse(manifest.is_artifact_user_owned("antios.config.json"))

        self.assertTrue(manifest.is_artifact_stale(".antios/stale.json"))
        self.assertFalse(manifest.is_artifact_stale("antios.config.json"))


if __name__ == "__main__":
    unittest.main()
