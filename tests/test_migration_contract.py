"""Tests for AntiOS 2.0 Phase 72: Compatibility & Migration Contract."""

from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.manifest import (
    CURRENT_ANTIOS_VERSION,
    CURRENT_SCHEMA_VERSION,
    ArtifactOwnership,
    ArtifactRecord,
    ProjectManifest,
    save_manifest,
)
from framework.core.migration import (
    CompatibilityState,
    MigrationEngine,
    MigrationPlan,
    MigrationResult,
    MigrationStep,
)


class TestMigrationContract(unittest.TestCase):
    """Unit tests for the Compatibility & Migration Engine."""

    def test_parse_semver(self):
        """Test SemVer parsing helper."""
        self.assertEqual(MigrationEngine.parse_semver("2.0.0"), (2, 0, 0))
        self.assertEqual(MigrationEngine.parse_semver("1.9.4-beta"), (1, 9, 4))
        self.assertEqual(MigrationEngine.parse_semver("v3.12.5"), (3, 12, 5))
        self.assertEqual(MigrationEngine.parse_semver("invalid"), (0, 0, 0))

    def test_assess_compatibility_unknown_if_no_manifest(self):
        """Assessing a folder without .antios/manifest.json returns UNKNOWN."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            state, reason, manifest = MigrationEngine.assess_compatibility(tmp_dir)
            self.assertEqual(state, CompatibilityState.UNKNOWN)
            self.assertIsNone(manifest)

    def test_assess_compatibility_corrupted_manifest(self):
        """Malformed JSON manifest returns CORRUPTED."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            antios_dir = Path(tmp_dir) / ".antios"
            antios_dir.mkdir(parents=True)
            (antios_dir / "manifest.json").write_text("{malformed: json", encoding="utf-8")

            state, reason, manifest = MigrationEngine.assess_compatibility(tmp_dir)
            self.assertEqual(state, CompatibilityState.CORRUPTED)
            self.assertIsNone(manifest)

    def test_assess_compatibility_incompatible_major(self):
        """Instance on older major version is marked INCOMPATIBLE."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version="1.5.0",
                schema_version=CURRENT_SCHEMA_VERSION,
                project_fingerprint="test-fp",
                source_revision="v1.5.0",
            )
            save_manifest(manifest, tmp_dir)

            state, reason, _ = MigrationEngine.assess_compatibility(
                target_root=tmp_dir,
                target_version="2.0.0",
            )
            self.assertEqual(state, CompatibilityState.INCOMPATIBLE)
            self.assertIn("Major version leap", reason)

    def test_assess_compatibility_schema_mismatch(self):
        """Instance with older schema version requires migration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version=CURRENT_ANTIOS_VERSION,
                schema_version="1.0.0",
                project_fingerprint="test-fp",
                source_revision="v2.0.0",
            )
            save_manifest(manifest, tmp_dir)

            state, reason, _ = MigrationEngine.assess_compatibility(
                target_root=tmp_dir,
                target_schema="2.0.0",
            )
            self.assertEqual(state, CompatibilityState.MIGRATION_REQUIRED)
            self.assertIn("Schema version mismatch", reason)

    def test_assess_compatibility_upgrade_available(self):
        """Instance on older minor/patch version indicates upgrade available."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version="2.0.0",
                schema_version=CURRENT_SCHEMA_VERSION,
                project_fingerprint="test-fp",
                source_revision="v2.0.0",
            )
            save_manifest(manifest, tmp_dir)

            state, reason, _ = MigrationEngine.assess_compatibility(
                target_root=tmp_dir,
                target_version="2.1.0",
            )
            self.assertEqual(state, CompatibilityState.UPGRADE_AVAILABLE)

    def test_assess_compatibility_compatible(self):
        """Instance with matching versions is COMPATIBLE."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version=CURRENT_ANTIOS_VERSION,
                schema_version=CURRENT_SCHEMA_VERSION,
                project_fingerprint="test-fp",
                source_revision="v2.0.0",
            )
            save_manifest(manifest, tmp_dir)

            state, reason, _ = MigrationEngine.assess_compatibility(tmp_dir)
            self.assertEqual(state, CompatibilityState.COMPATIBLE)

    def test_plan_migration_incompatible_fails_closed(self):
        """Planning migration for incompatible instance produces non-executable plan."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version="1.0.0",
                schema_version="1.0.0",
                project_fingerprint="test-fp",
                source_revision="v1.0.0",
            )
            save_manifest(manifest, tmp_dir)

            plan = MigrationEngine.plan_migration(
                target_root=tmp_dir,
                target_version="2.0.0",
                target_schema="2.0.0",
            )
            self.assertFalse(plan.is_executable)
            self.assertEqual(len(plan.steps), 0)
            self.assertTrue(len(plan.conflicts) > 0)

    def test_execute_migration_schema_upgrade_in_tempdir(self):
        """Test executing a migration plan that upgrades schema version."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = ProjectManifest(
                antios_version="2.0.0",
                schema_version="1.0.0",
                project_fingerprint="test-fp",
                source_revision="v2.0.0",
                capability_revision="1.0",
            )
            save_manifest(manifest, tmp_dir)

            plan = MigrationPlan(
                plan_id="plan-test-01",
                target_root=tmp_dir,
                source_version="2.0.0",
                instance_version="2.0.0",
                source_schema="2.0.0",
                instance_schema="1.0.0",
                compatibility_state=CompatibilityState.MIGRATION_REQUIRED,
                steps=[
                    MigrationStep(
                        step_id="step-1",
                        action="SCHEMA_UPGRADE",
                        target_path=".antios/manifest.json",
                        description="Upgrade schema",
                    )
                ],
                conflicts=[],
                is_executable=True,
            )

            result = MigrationEngine.execute_migration(plan, dry_run=False)
            self.assertTrue(result.is_successful)
            self.assertEqual(result.final_state, CompatibilityState.COMPATIBLE)

            # Check updated manifest on disk
            updated_state, _, updated_manifest = MigrationEngine.assess_compatibility(tmp_dir)
            self.assertEqual(updated_state, CompatibilityState.COMPATIBLE)
            self.assertIsNotNone(updated_manifest)
            self.assertEqual(updated_manifest.schema_version, "2.0.0")
            self.assertEqual(updated_manifest.capability_revision, "1.1")


if __name__ == "__main__":
    unittest.main()
