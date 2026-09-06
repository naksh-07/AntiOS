"""Productization & Hardened Lifecycle tests for AntiOS 2.0."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from framework.core.doctor import DoctorEngine, redact_secrets
from framework.core.installation import InstallationLifecycleManager
from framework.core.manifest import InstallationState, load_manifest
from framework.core.version import ANTIOS_VERSION


class TestLifecycleProductization(unittest.TestCase):
    """Verifies hardened installation, update, rollback, repair, and remove lifecycles."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_root = Path(self.temp_dir.name)
        self.source_root = Path(__file__).resolve().parent.parent

        # Setup minimal synthetic target project
        (self.target_root / "pyproject.toml").write_text(
            '[project]\nname = "my-test-app"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        (self.target_root / "src").mkdir(parents=True, exist_ok=True)
        self.user_source_file = self.target_root / "src/app.py"
        self.user_source_file.write_text("print('user project code')\n", encoding="utf-8")

        self.mgr = InstallationLifecycleManager(
            source_root=self.source_root,
            target_root=self.target_root,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fresh_install_and_idempotency(self):
        """Fresh install succeeds; repeated install is idempotent with zero file mutations."""
        res1 = self.mgr.install()
        self.assertEqual(res1.status, "SUCCESS")
        self.assertEqual(res1.installation_state, InstallationState.INSTALLED)
        self.assertTrue((self.target_root / ".antios/manifest.json").exists())
        self.assertTrue((self.target_root / "antios.config.json").exists())
        self.assertTrue((self.target_root / ".agents/skills/antios/SKILL.md").exists())

        # Second install should be idempotent
        res2 = self.mgr.install()
        self.assertEqual(res2.status, "IDEMPOTENT")
        self.assertEqual(len(res2.written_files), 0)

    def test_downgrade_prevention(self):
        """Attempting to install an older version is blocked unless force_downgrade is enabled."""
        self.mgr.install()

        # Try downgrade without force_downgrade
        res_down = self.mgr.install(target_version="1.0.0", force_downgrade=False)
        self.assertEqual(res_down.status, "BLOCKED")
        self.assertIn("Downgrade rejected", res_down.issues[0])

        # Overwrite with force_downgrade
        res_force = self.mgr.install(target_version="1.0.0", force_downgrade=True, force=True)
        self.assertEqual(res_force.status, "SUCCESS")

    def test_update_creates_snapshot_and_updates(self):
        """Update creates a snapshot in .antios/backups and synchronizes instance files."""
        self.mgr.install()
        manifest = load_manifest(self.target_root)
        self.assertIsNotNone(manifest)

        # Execute update
        res_up = self.mgr.update(new_revision="v2.1.0-beta.2")
        self.assertEqual(res_up.status, "SUCCESS")

        # Snapshot should exist in .antios/backups
        backup_dir = self.target_root / ".antios/backups"
        self.assertTrue(backup_dir.is_dir())
        snaps = list(backup_dir.glob("snapshot_*.json"))
        self.assertGreaterEqual(len(snaps), 1)

    def test_rollback_restores_instance_and_preserves_user_code(self):
        """Rollback restores prior snapshot and NEVER mutates user application code."""
        self.mgr.install()

        # Modify user project code
        self.user_source_file.write_text("print('user modified business logic')\n", encoding="utf-8")

        # Update creates snapshot
        self.mgr.update(new_revision="v2.1.0")

        # Rollback
        res_roll = self.mgr.rollback()
        self.assertEqual(res_roll.status, "SUCCESS")

        # User source file must remain intact
        self.assertEqual(
            self.user_source_file.read_text(encoding="utf-8"),
            "print('user modified business logic')\n",
        )

        # Manifest must be restored
        manifest = load_manifest(self.target_root)
        self.assertIsNotNone(manifest)

    def test_repair_plan_and_apply(self):
        """Repair can plan restoration without mutating, then apply restoration cleanly."""
        self.mgr.install()

        # Delete a managed file
        target_guard = self.target_root / ".antios/runtime/pre_tool_guard.py"
        self.assertTrue(target_guard.is_file())
        target_guard.unlink()

        # Plan only
        res_plan = self.mgr.repair(plan_only=True)
        self.assertEqual(res_plan.status, "SUCCESS")
        self.assertIn(".antios/runtime/pre_tool_guard.py", res_plan.written_files)
        self.assertFalse(target_guard.exists())

        # Apply repair
        res_apply = self.mgr.repair(plan_only=False)
        self.assertEqual(res_apply.status, "SUCCESS")
        self.assertTrue(target_guard.is_file())

    def test_remove_cleanliness_and_user_preservation(self):
        """Remove deletes AntiOS assets, verifies cleanup, and strictly preserves user files."""
        self.mgr.install()
        self.assertTrue((self.target_root / ".antios").exists())

        # Remove
        res_rem = self.mgr.remove()
        self.assertEqual(res_rem.status, "SUCCESS")
        self.assertFalse((self.target_root / ".antios").exists())
        self.assertFalse((self.target_root / "antios.config.json").exists())

        # User source file and pyproject.toml MUST still exist
        self.assertTrue(self.user_source_file.exists())
        self.assertTrue((self.target_root / "pyproject.toml").exists())

        # Repeated remove should be clean no-op
        res_rem2 = self.mgr.remove()
        self.assertEqual(res_rem2.status, "SUCCESS")

    def test_doctor_and_secret_redaction(self):
        """Doctor inspects health and automated filter redacts tokens/secrets."""
        self.mgr.install()
        doc_eng = DoctorEngine(self.target_root)
        rep = doc_eng.run_doctor()
        self.assertTrue(rep.is_healthy)
        self.assertGreater(rep.passed_checks, 0)

        # Secret redaction filter
        leak_text = "token: gho_ABC1234567890123456789012345678901234567 password=supersecret123"
        redacted = redact_secrets(leak_text)
        self.assertNotIn("gho_ABC1234567890", redacted)
        self.assertNotIn("supersecret123", redacted)
        self.assertIn("REDACTED", redacted)


if __name__ == "__main__":
    unittest.main()
