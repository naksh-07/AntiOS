"""End-to-End Beta Proving Ground: Productization, Release Engineering & Lifecycle Validation.

Executes the complete canonical beta product lifecycle in an isolated sandbox:
1. Fresh installation -> 2. Verify -> 3. Adapt fresh project -> 4. Run mission ->
5. Detect issue -> 6. Create issue card -> 7. Apply fix -> 8. Verify fix ->
9. Release preparation check -> 10. Update instance -> 11. Rollback instance ->
12. Repair instance -> 13. Remove AntiOS -> 14. Verify clean post-removal state.

Strict Isolation Invariant:
- Operates entirely inside tempfile.TemporaryDirectory.
- Zero touch or modification of StudyLab production or StudySourceCore.
"""

from pathlib import Path
import shutil
import tempfile
import unittest

from framework.cli import build_parser, main
from framework.core.doctor import DoctorEngine
from framework.core.github_capability import GitHubCapabilityEngine, IssueClass, IssueEvidence
from framework.core.installation import InstallationLifecycleManager
from framework.core.manifest import InstallationState, load_manifest
from framework.core.version import ANTIOS_VERSION


class TestBetaProductizationE2E(unittest.TestCase):
    """Full End-to-End proving ground scenario for AntiOS Beta readiness."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sandbox_root = Path(self.temp_dir.name)
        self.source_root = Path(__file__).resolve().parent.parent

        # Setup isolated synthetic target project (Python + test suite)
        (self.sandbox_root / "pyproject.toml").write_text(
            '[project]\nname = "beta-sandbox-app"\nversion = "1.0.0"\n'
            'dependencies = []\n',
            encoding="utf-8",
        )
        src_dir = self.sandbox_root / "src/beta_pkg"
        src_dir.mkdir(parents=True, exist_ok=True)
        self.app_file = src_dir / "calculator.py"
        self.app_file.write_text(
            "def add(a: int, b: int) -> int:\n    return a + b\n",
            encoding="utf-8",
        )

        test_dir = self.sandbox_root / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        self.test_file = test_dir / "test_calculator.py"
        self.test_file.write_text(
            "import unittest\nfrom src.beta_pkg.calculator import add\n\n"
            "class TestCalc(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_beta_lifecycle_proving_ground(self):
        """Executes the complete 14-step Beta Readiness Lifecycle."""
        mgr = InstallationLifecycleManager(
            source_root=self.source_root,
            target_root=self.sandbox_root,
        )

        # 1. Fresh installation
        res_inst = mgr.install()
        self.assertEqual(res_inst.status, "SUCCESS")
        self.assertEqual(res_inst.installation_state, InstallationState.INSTALLED)
        self.assertTrue((self.sandbox_root / ".antios/manifest.json").exists())
        self.assertTrue((self.sandbox_root / "antios.config.json").exists())

        # 2. Verify
        res_ver = mgr.verify()
        self.assertEqual(res_ver.status, "SUCCESS")

        # 3. Adapt fresh project
        res_adapt = mgr.adapt()
        self.assertEqual(res_adapt.status, "SUCCESS")

        # 4. Run Mission: Add subtract functionality to target application
        self.app_file.write_text(
            "def add(a: int, b: int) -> int:\n    return a + b\n\n"
            "def subtract(a: int, b: int) -> int:\n    return a - b\n",
            encoding="utf-8",
        )

        # 5. Detect Issue: Unit test missing for subtract
        has_sub_test = "test_sub" in self.test_file.read_text(encoding="utf-8")
        self.assertFalse(has_sub_test)

        # 6. Create Issue Card
        gh_eng = GitHubCapabilityEngine(self.sandbox_root)
        issue = IssueEvidence(
            title="Missing test coverage for subtract() function",
            issue_class=IssueClass.BUG,
            observed_behavior="subtract() is implemented without test coverage",
            expected_behavior="Unit test test_subtract() validates subtraction",
            reproduction_steps=["Run test suite"],
            evidence_traces=["test_calculator.py lacks test_sub"],
            affected_files=["tests/test_calculator.py"],
            anti_os_version=ANTIOS_VERSION,
        )
        issue_md = issue.to_markdown()
        self.assertIn("Missing test coverage", issue_md)

        # 7. Apply Fix: Add test for subtract
        self.test_file.write_text(
            "import unittest\nfrom src.beta_pkg.calculator import add, subtract\n\n"
            "class TestCalc(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n"
            "    def test_sub(self):\n"
            "        self.assertEqual(subtract(5, 2), 3)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

        # 8. Verify Fix
        doc_eng = DoctorEngine(self.sandbox_root)
        rep = doc_eng.run_doctor()
        self.assertTrue(rep.is_healthy)

        # 9. Release preparation check via CLI
        code_ver = main(["version", "--path", str(self.sandbox_root)])
        self.assertEqual(code_ver, 0)

        code_stat = main(["status", "--path", str(self.sandbox_root)])
        self.assertEqual(code_stat, 0)

        # 10. Update instance to new revision
        res_upd = mgr.update(new_revision="v2.0.0-beta.2")
        self.assertEqual(res_upd.status, "SUCCESS")
        self.assertTrue((self.sandbox_root / ".antios/backups").is_dir())

        # 11. Rollback instance to pre-update snapshot
        res_roll = mgr.rollback()
        self.assertEqual(res_roll.status, "SUCCESS")
        # Ensure user application code was strictly preserved during rollback
        self.assertIn("def subtract", self.app_file.read_text(encoding="utf-8"))
        self.assertIn("test_sub", self.test_file.read_text(encoding="utf-8"))

        # 12. Repair instance
        # Deliberately remove pre_tool_guard.py to simulate partial file corruption
        guard_file = self.sandbox_root / ".antios/runtime/pre_tool_guard.py"
        guard_file.unlink()
        self.assertFalse(guard_file.exists())

        res_rep = mgr.repair()
        self.assertEqual(res_rep.status, "SUCCESS")
        self.assertTrue(guard_file.exists())

        # 13. Remove AntiOS
        res_rem = mgr.remove()
        self.assertEqual(res_rem.status, "SUCCESS")

        # 14. Verify clean post-removal state
        self.assertFalse((self.sandbox_root / ".antios").exists())
        self.assertFalse((self.sandbox_root / "antios.config.json").exists())
        # Target project business logic and tests must remain 100% intact!
        self.assertTrue(self.app_file.exists())
        self.assertTrue(self.test_file.exists())
        self.assertTrue((self.sandbox_root / "pyproject.toml").exists())


if __name__ == "__main__":
    unittest.main()
