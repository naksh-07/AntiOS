"""Unit tests for AntiOS 2.0 Project Boundary Compiler."""

import json
from pathlib import Path
import tempfile
import unittest

from framework.core.compiler import ProjectBoundaryCompiler
from framework.core.config import AntiOSConfig, RunnerConfig
from framework.core.manifest import InstallationState, load_manifest


class TestBoundaryCompiler(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.target_root = Path(self.tmpdir.name)
        self.source_root = Path(__file__).resolve().parent.parent

        # Create minimal target project fixture
        (self.target_root / "pyproject.toml").write_text(
            '[project]\nname = "my-service"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        src_dir = self.target_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "service.py").write_text("def run(): pass\n", encoding="utf-8")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_compiler_generates_standard_instance_assets(self):
        compiler = ProjectBoundaryCompiler(
            source_root=self.source_root,
            target_root=self.target_root,
            source_revision="v2.0.0-test",
        )
        result = compiler.compile()
        self.assertTrue(result.success)

        expected_assets = {
            ".antios/manifest.json",
            ".antios/project_profile.json",
            ".antios/knowledge.json",
            ".antios/agent_topology.json",
            ".antios/tool_policy.json",
            ".agents/skills/antios/SKILL.md",
            ".agents/hooks.json",
            "antios.config.json",
        }
        for asset in expected_assets:
            self.assertIn(asset, result.compiled_files, f"Missing compiled asset: {asset}")

        # Verify manifest content
        manifest = result.manifest
        self.assertEqual(manifest.source_revision, "v2.0.0-test")
        self.assertTrue(len(manifest.project_fingerprint) > 0)
        self.assertIn("antios.config.json", manifest.managed_paths)
        self.assertIn(".antios/knowledge.json", manifest.generated_paths)

    def test_compiler_strictly_excludes_development_material(self):
        compiler = ProjectBoundaryCompiler(
            source_root=self.source_root,
            target_root=self.target_root,
        )
        result = compiler.compile()

        # Verify no test suites, reports, archives, or internal git files are compiled
        for compiled_path in result.compiled_files.keys():
            self.assertFalse(compiled_path.startswith("tests/"), f"Leaked test path: {compiled_path}")
            self.assertFalse(compiled_path.startswith("reports/"), f"Leaked report path: {compiled_path}")
            self.assertFalse(compiled_path.startswith("sandbox/"), f"Leaked sandbox path: {compiled_path}")
            self.assertFalse(compiled_path.startswith(".git/"), f"Leaked git path: {compiled_path}")

    def test_compiler_emit_writes_files_deterministically(self):
        compiler = ProjectBoundaryCompiler(
            source_root=self.source_root,
            target_root=self.target_root,
        )
        result = compiler.compile()
        success, written, conflicts = compiler.emit(result)

        self.assertTrue(success)
        self.assertEqual(len(conflicts), 0)
        self.assertTrue((self.target_root / ".antios/manifest.json").is_file())
        self.assertTrue((self.target_root / ".agents/skills/antios/SKILL.md").is_file())
        self.assertTrue((self.target_root / "antios.config.json").is_file())

        # Validate loaded manifest from disk
        loaded_manifest = load_manifest(self.target_root)
        self.assertIsNotNone(loaded_manifest)
        self.assertEqual(loaded_manifest.installation_state, InstallationState.INSTALLED)

    def test_compiler_respects_custom_config_override(self):
        custom_config = AntiOSConfig(
            name="Custom-Service-Adapter",
            protected_domain_paths=["src/core_engine"],
            test_runners=[
                RunnerConfig(
                    name="pytest-custom",
                    manifest="pyproject.toml",
                    default_command=["pytest", "-m", "unit"],
                    timeout_seconds=45,
                )
            ],
        )

        compiler = ProjectBoundaryCompiler(
            source_root=self.source_root,
            target_root=self.target_root,
        )
        result = compiler.compile(config_override=custom_config)

        self.assertIn("src/core_engine", result.manifest.protected_paths)
        # Check tool policy includes custom runner
        tool_policy = json.loads(result.compiled_files[".antios/tool_policy.json"])
        runner_names = [r["name"] for r in tool_policy["configured_runners"]]
        self.assertIn("pytest-custom", runner_names)


if __name__ == "__main__":
    unittest.main()
