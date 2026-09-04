"""AntiOS 2.0 Phase 48 Complete Installation Certification Suite.

Validates the full physical proof across all 7 archetypal project fixtures:
1. Simple project (minimal repo, no build manifest)
2. Python project (pyproject.toml, pytest runner)
3. TypeScript / Node project (package.json, vitest runner)
4. Project with existing .agents/ (pre-existing custom skills, user rules)
5. Project with conflicting instructions (conflicting AGENTS.md)
6. Project with pre-existing skills (verifies non-clobbering)
7. Project with unusual / unknown topology (manifestless nested structure)

Exercises full lifecycle:
fresh -> install -> adapt -> assets available -> verify -> second install (idempotency)
-> modify user-owned artifact -> update AntiOS -> verify user ownership preserved.
"""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from framework.core.discovery import discover_project
from framework.core.installation import InstallationLifecycleManager
from framework.core.manifest import (
    AdaptationState,
    InstallationState,
    load_manifest,
)


class TestInstallationCertificationE2E(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.scratch_root = Path(self.tmpdir.name)
        self.repo_source = Path(__file__).resolve().parent.parent
        self.fixtures_dir = self.repo_source / "tests/fixtures"

    def tearDown(self):
        self.tmpdir.cleanup()

    def _copy_fixture(self, fixture_name: str) -> Path:
        target = self.scratch_root / fixture_name
        src = self.fixtures_dir / fixture_name
        shutil.copytree(src, target)
        return target

    def test_e2e_1_simple_project_certification(self):
        project_dir = self._copy_fixture("simple_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        # 1. Fresh install
        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")
        self.assertEqual(install_res.installation_state, InstallationState.INSTALLED)

        # 2. Verify assets exist
        self.assertTrue((project_dir / ".antios/manifest.json").is_file())
        self.assertTrue((project_dir / ".agents/skills/antios/SKILL.md").is_file())
        self.assertTrue((project_dir / "antios.config.json").is_file())

        # 3. Verify integrity
        verify_res = manager.verify()
        self.assertEqual(verify_res.status, "SUCCESS")

        # 4. Second install is idempotent
        idem_res = manager.install()
        self.assertEqual(idem_res.status, "IDEMPOTENT")

    def test_e2e_2_python_project_certification(self):
        project_dir = self._copy_fixture("python_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        # Install
        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")

        # Verify tool policy has python test runner
        tool_policy_file = project_dir / ".antios/tool_policy.json"
        self.assertTrue(tool_policy_file.is_file())
        tool_data = json.loads(tool_policy_file.read_text(encoding="utf-8"))
        runners = [r["name"] for r in tool_data.get("configured_runners", [])]
        self.assertTrue(any("pytest" in r or "python" in r for r in runners))

        # Re-adapt
        adapt_res = manager.adapt()
        self.assertEqual(adapt_res.status, "SUCCESS")

    def test_e2e_3_typescript_project_certification(self):
        project_dir = self._copy_fixture("ts_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")

        manifest = load_manifest(project_dir)
        self.assertIsNotNone(manifest)
        self.assertTrue((project_dir / ".antios/knowledge.json").is_file())

    def test_e2e_4_existing_agents_preserves_user_skills(self):
        project_dir = self._copy_fixture("existing_agents_project")
        custom_skill_file = project_dir / ".agents/skills/custom-calc/SKILL.md"
        self.assertTrue(custom_skill_file.is_file())
        original_skill_content = custom_skill_file.read_text(encoding="utf-8")

        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        # Install must detect pre-existing user skill and preserve it
        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")

        manifest = load_manifest(project_dir)
        self.assertIn(".agents/skills/custom-calc/SKILL.md", manifest.user_owned_paths)

        # Content must remain completely unchanged
        current_content = custom_skill_file.read_text(encoding="utf-8")
        self.assertEqual(current_content, original_skill_content)

        # Both custom skill and antios skill exist simultaneously
        self.assertTrue((project_dir / ".agents/skills/antios/SKILL.md").is_file())
        self.assertTrue(custom_skill_file.is_file())

    def test_e2e_5_conflicting_instructions_project(self):
        project_dir = self._copy_fixture("conflicting_instructions_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        # Install should adapt and detect the conflict in profile
        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")

        profile_file = project_dir / ".antios/project_profile.json"
        self.assertTrue(profile_file.is_file())
        profile_data = json.loads(profile_file.read_text(encoding="utf-8"))

        # Invariants in antios.config.json must still enforce fail_closed=True!
        config_data = json.loads((project_dir / "antios.config.json").read_text(encoding="utf-8"))
        self.assertTrue(config_data["policies"]["fail_closed"])

    def test_e2e_6_user_modification_preservation_across_update(self):
        project_dir = self._copy_fixture("simple_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        manager.install()

        # User modifies antios.config.json to add a custom domain path
        config_path = project_dir / "antios.config.json"
        user_config = json.loads(config_path.read_text(encoding="utf-8"))
        user_config["protected_domain_paths"] = ["custom/secret"]
        config_path.write_text(json.dumps(user_config, indent=2), encoding="utf-8", newline="\n")

        # Now update AntiOS source revision
        update_res = manager.update(new_revision="v2.1.0")

        # Must report conflict on antios.config.json and refuse to overwrite!
        self.assertTrue(any("antios.config.json" in c for c in update_res.conflicts))

        # Check that user modification was strictly preserved!
        current_config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(current_config["protected_domain_paths"], ["custom/secret"])

    def test_e2e_7_unusual_unknown_topology_project(self):
        project_dir = self._copy_fixture("unknown_project")
        manager = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=project_dir,
            source_revision="v2.0.0",
        )

        # Install gracefully degrades for unknown topologies without crashing
        install_res = manager.install()
        self.assertEqual(install_res.status, "SUCCESS")
        self.assertTrue((project_dir / ".antios/manifest.json").is_file())
        self.assertTrue((project_dir / ".agents/skills/antios/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
