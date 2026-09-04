"""Unit tests for AntiOS 2.0 Installation Lifecycle Engine."""

import json
from pathlib import Path
import tempfile
import unittest

from framework.core.installation import InstallationLifecycleManager
from framework.core.manifest import (
    AdaptationState,
    InstallationState,
    load_manifest,
)


class TestInstallationLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.target_root = Path(self.tmpdir.name)
        self.source_root = Path(__file__).resolve().parent.parent

        # Scaffold a minimal Python project fixture
        (self.target_root / "pyproject.toml").write_text(
            '[project]\nname = "demo-app"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        src_dir = self.target_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "app.py").write_text("print('running')\n", encoding="utf-8")

        self.manager = InstallationLifecycleManager(
            source_root=self.source_root,
            target_root=self.target_root,
            source_revision="v2.0.0",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_fresh_install_lifecycle(self):
        res = self.manager.install()
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.installation_state, InstallationState.INSTALLED)
        self.assertEqual(res.adaptation_state, AdaptationState.ADAPTED)
        self.assertTrue(len(res.written_files) >= 7)

        # Verify manifest on disk
        manifest = load_manifest(self.target_root)
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.installation_state, InstallationState.INSTALLED)
        self.assertTrue((self.target_root / ".agents/skills/antios/SKILL.md").is_file())
        self.assertTrue((self.target_root / "antios.config.json").is_file())

    def test_second_install_is_idempotent(self):
        # First install
        res1 = self.manager.install()
        self.assertEqual(res1.status, "SUCCESS")

        # Second install without changes
        res2 = self.manager.install()
        self.assertEqual(res2.status, "IDEMPOTENT")
        self.assertEqual(len(res2.written_files), 0)

    def test_user_modified_managed_file_blocks_overwrite_and_surfaces_conflict(self):
        # First install
        self.manager.install()

        # User modifies antios.config.json
        config_path = self.target_root / "antios.config.json"
        config_path.write_text('{"name": "user-modified-config"}', encoding="utf-8")

        # Re-running install must detect conflict and refuse to overwrite
        res = self.manager.install()
        self.assertIn(res.status, ("CONFLICT", "STALE", "BLOCKED"))
        if res.conflicts:
            self.assertTrue(any("modified by the user" in c for c in res.conflicts))

        # Verify file on disk was NOT silently overwritten
        content = config_path.read_text(encoding="utf-8")
        self.assertIn("user-modified-config", content)

    def test_adapt_updates_fingerprint_and_intelligence(self):
        self.manager.install()

        # Add a new dependency / manifest change
        (self.target_root / "package.json").write_text('{"name": "frontend"}\n', encoding="utf-8")

        # Run adapt
        adapt_res = self.manager.adapt()
        self.assertEqual(adapt_res.status, "SUCCESS")
        self.assertEqual(adapt_res.adaptation_state, AdaptationState.ADAPTED)

        manifest = load_manifest(self.target_root)
        profile_path = self.target_root / ".antios/project_profile.json"
        self.assertTrue(profile_path.is_file())

    def test_update_lifecycle_advances_source_revision(self):
        self.manager.install()

        update_res = self.manager.update(new_revision="v2.1.0-alpha")
        self.assertEqual(update_res.status, "SUCCESS")

        manifest = load_manifest(self.target_root)
        self.assertEqual(manifest.source_revision, "v2.1.0-alpha")

    def test_repair_lifecycle_restores_missing_files_preserving_user_files(self):
        self.manager.install()

        # User creates a custom script
        user_script = self.target_root / "src/custom_tool.py"
        user_script.write_text("# custom code", encoding="utf-8")

        # Accidental deletion of generated file
        skill_file = self.target_root / ".agents/skills/antios/SKILL.md"
        skill_file.unlink()
        self.assertFalse(skill_file.exists())

        # Run repair
        repair_res = self.manager.repair()
        self.assertEqual(repair_res.status, "SUCCESS")
        self.assertTrue(skill_file.exists())
        self.assertTrue(user_script.exists())  # User script untouched

    def test_remove_lifecycle_cleans_antios_assets_preserving_user_project(self):
        self.manager.install()

        # User creates an app file and a custom agent skill
        custom_skill = self.target_root / ".agents/skills/custom/SKILL.md"
        custom_skill.parent.mkdir(parents=True, exist_ok=True)
        custom_skill.write_text("# Custom Skill", encoding="utf-8")

        remove_res = self.manager.remove()
        self.assertEqual(remove_res.status, "SUCCESS")
        self.assertEqual(remove_res.installation_state, InstallationState.REMOVED)

        # AntiOS assets removed
        self.assertFalse((self.target_root / ".antios").exists())
        self.assertFalse((self.target_root / ".agents/skills/antios").exists())

        # Project and user assets strictly preserved!
        self.assertTrue((self.target_root / "pyproject.toml").exists())
        self.assertTrue((self.target_root / "src/app.py").exists())
        self.assertTrue(custom_skill.exists())

    def test_corrupted_manifest_fails_closed(self):
        self.manager.install()

        manifest_path = self.target_root / ".antios/manifest.json"
        manifest_path.write_text("CORRUPTED_NON_JSON", encoding="utf-8")

        res = self.manager.install()
        self.assertEqual(res.status, "BLOCKED")
        self.assertEqual(res.installation_state, InstallationState.ERROR)
        self.assertTrue(any("Corrupted manifest" in issue for issue in res.issues))


if __name__ == "__main__":
    unittest.main()
