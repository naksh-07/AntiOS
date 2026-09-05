"""AntiOS 2.0 - Phases 79–82 Comprehensive Runtime Closure Verification Suite.

Validates the constitutional invariant SOURCE ? INSTANCE:
- The compiled Project Agent OS instance is completely self-contained.
- Zero dependencies on AntiOS source repository, framework/, tests/, or development assets.
- AST parsing verifies zero imports from 'framework' across all runtime scripts.
- Physical execution of pre_tool_guard.py and stop_gate.py in clean isolated subprocesses.
- Architecture wayfinder inspect_instance.py operation.
- Lifecycle idempotency, repair, and clean removal.
- Multi-archetype closure across Python, Node, and Rust targets.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from framework.core.compiler import ProjectBoundaryCompiler
from framework.core.installation import InstallationLifecycleManager
from framework.core.runtime_contract import (
    REQUIRED_INSTANCE_ARTIFACTS,
    REQUIRED_RUNTIME_SCRIPTS,
    FORBIDDEN_SOURCE_PATTERNS,
    RuntimeClosureResult,
    check_ast_for_framework_imports,
    verify_runtime_closure,
)


class TestRuntimeClosure(unittest.TestCase):
    """Authoritative test suite for Project Instance Runtime Closure."""

    def setUp(self):
        self.source_root = Path(__file__).resolve().parent.parent

    def _install_fixture(self, target_root: Path, archetype: str = "PYTHON") -> InstallationLifecycleManager:
        """Helper to create and compile a clean target project."""
        if archetype == "PYTHON":
            (target_root / "pyproject.toml").write_text(
                '[project]\nname = "sample-python"\nversion = "0.1.0"\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
                encoding="utf-8",
            )
            (target_root / "src").mkdir(parents=True, exist_ok=True)
            (target_root / "src" / "main.py").write_text('def add(a, b):\n    return a + b\n', encoding="utf-8")
            (target_root / "tests").mkdir(parents=True, exist_ok=True)
            (target_root / "tests" / "test_main.py").write_text(
                'from src.main import add\ndef test_add():\n    assert add(1, 2) == 3\n', encoding="utf-8"
            )
        elif archetype == "NODE":
            (target_root / "package.json").write_text(
                json.dumps({
                    "name": "sample-node",
                    "version": "1.0.0",
                    "scripts": {"test": "echo 'node tests pass' && exit 0"},
                }, indent=2),
                encoding="utf-8",
            )
            (target_root / "src").mkdir(parents=True, exist_ok=True)
            (target_root / "src" / "index.js").write_text('console.log("hello");\n', encoding="utf-8")
        elif archetype == "RUST":
            (target_root / "Cargo.toml").write_text(
                '[package]\nname = "sample-rust"\nversion = "0.1.0"\nedition = "2021"\n', encoding="utf-8"
            )
            (target_root / "src").mkdir(parents=True, exist_ok=True)
            (target_root / "src" / "main.rs").write_text('fn main() {}\n', encoding="utf-8")

        mgr = InstallationLifecycleManager(
            source_root=self.source_root,
            target_root=target_root,
            source_revision="v2.0.0-test",
        )
        res = mgr.install()
        self.assertEqual(res.status, "SUCCESS", f"Installation failed: {res.issues} {res.conflicts}")
        return mgr

    def test_all_required_instance_artifacts_and_runtime_scripts_created(self):
        """Verifies that compiling a project creates all required instance artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            for rel_path in REQUIRED_INSTANCE_ARTIFACTS:
                artifact_path = target_root / rel_path
                self.assertTrue(
                    artifact_path.is_file(),
                    f"Required instance artifact missing on disk: '{rel_path}'"
                )

            for rel_script in REQUIRED_RUNTIME_SCRIPTS:
                script_path = target_root / rel_script
                self.assertTrue(
                    script_path.is_file(),
                    f"Required runtime script missing on disk: '{rel_script}'"
                )

            # Framework development tree MUST NOT be copied
            self.assertFalse((target_root / "framework" / "core").is_dir())
            self.assertFalse((target_root / "framework" / "scripts").is_dir())
            self.assertFalse((target_root / ".agents" / "workflows").is_dir())

    def test_verify_runtime_closure_contract_passes(self):
        """Verifies that verify_runtime_closure engine validates the compiled instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            result = verify_runtime_closure(target_root, execute_guards=False)
            self.assertTrue(
                result.is_closed,
                f"Runtime closure verification failed with violations: {result.violations}"
            )
            self.assertEqual(len(result.violations), 0)
            self.assertEqual(len(result.missing_artifacts), 0)

    def test_zero_framework_imports_in_runtime_scripts(self):
        """Verifies via AST that no .antios/runtime/*.py file imports from 'framework'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            runtime_dir = target_root / ".antios" / "runtime"
            self.assertTrue(runtime_dir.is_dir())

            for script in runtime_dir.glob("*.py"):
                issues = check_ast_for_framework_imports(script)
                self.assertEqual(
                    issues,
                    [],
                    f"Runtime script '{script.name}' imports from forbidden framework: {issues}"
                )

    def test_zero_source_leak_patterns_in_compiled_artifacts(self):
        """Verifies that forbidden source leak patterns do not appear in instance files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            for rel_path in REQUIRED_INSTANCE_ARTIFACTS:
                if rel_path.endswith("verify_runtime.py"):
                    continue
                p = target_root / rel_path
                content = p.read_text(encoding="utf-8")
                for pattern, reason in FORBIDDEN_SOURCE_PATTERNS:
                    if pattern == "tests/run_all.py" and rel_path == "antios.config.json":
                        continue
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Found forbidden source leak '{pattern}' in '{rel_path}' ({reason})"
                    )

    def test_instance_local_verify_runtime_script_execution(self):
        """Executes .antios/runtime/verify_runtime.py in isolated subprocess with zero PYTHONPATH."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            verifier_script = target_root / ".antios" / "runtime" / "verify_runtime.py"
            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            proc = subprocess.run(
                [sys.executable, str(verifier_script)],
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(
                proc.returncode,
                0,
                f"verify_runtime.py failed with code {proc.returncode}.\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
            )
            self.assertIn("[PASS] Instance is self-contained", proc.stdout)

    def test_pre_tool_guard_allows_application_writes(self):
        """Verifies that pre_tool_guard.py allows writes to normal project files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            guard_script = target_root / ".antios" / "runtime" / "pre_tool_guard.py"
            payload = json.dumps({
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "src/new_module.py"},
                },
                "workspacePaths": [str(target_root)],
            })

            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            proc = subprocess.run(
                [sys.executable, str(guard_script)],
                input=payload,
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "allow")

    def test_pre_tool_guard_denies_protected_zones(self):
        """Verifies that pre_tool_guard.py blocks modifications to protected zones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            guard_script = target_root / ".antios" / "runtime" / "pre_tool_guard.py"
            protected_targets = [
                ".agents/hooks.json",
                ".agents/skills/antios/SKILL.md",
                ".antios/manifest.json",
                ".antios/runtime/stop_gate.py",
                "antios.config.json",
                ".git/config",
            ]

            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            for pt in protected_targets:
                payload = json.dumps({
                    "toolCall": {
                        "name": "replace_file_content",
                        "args": {"TargetFile": pt},
                    },
                    "workspacePaths": [str(target_root)],
                })
                proc = subprocess.run(
                    [sys.executable, str(guard_script)],
                    input=payload,
                    cwd=str(target_root),
                    env=clean_env,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(proc.returncode, 0)
                data = json.loads(proc.stdout)
                self.assertEqual(
                    data.get("decision"),
                    "deny",
                    f"Expected DENY for protected target '{pt}', got: {data}"
                )
                self.assertIn("strictly forbidden", data.get("reason", ""))

    def test_pre_tool_guard_denies_path_traversal(self):
        """Verifies that pre_tool_guard.py blocks path traversal attempts outside workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            guard_script = target_root / ".antios" / "runtime" / "pre_tool_guard.py"
            payload = json.dumps({
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "../../outside_workspace.txt"},
                },
                "workspacePaths": [str(target_root)],
            })

            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            proc = subprocess.run(
                [sys.executable, str(guard_script)],
                input=payload,
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "deny")
            self.assertIn("outside the workspace", data.get("reason", "").lower())

    def test_pre_tool_guard_fail_closed_on_invalid_input(self):
        """Verifies that pre_tool_guard.py fails closed when provided invalid or empty stdin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            guard_script = target_root / ".antios" / "runtime" / "pre_tool_guard.py"
            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            # Empty stdin fails closed with deny
            proc = subprocess.run(
                [sys.executable, str(guard_script)],
                input="",
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "deny")

            # Corrupted json stdin fails closed with deny
            proc = subprocess.run(
                [sys.executable, str(guard_script)],
                input="{bad-json",
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "deny")

    def test_stop_gate_detects_git_conflict_markers(self):
        """Verifies that stop_gate.py catches unresolved git conflict markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            # Inject git conflict marker in application file
            conflict_file = target_root / "src" / "conflict.py"
            conflict_marker_content = ("<" * 7) + " HEAD\nval = 1\n" + ("=" * 7) + "\nval = 2\n" + (">" * 7) + " branch\n"
            conflict_file.write_text(conflict_marker_content, encoding="utf-8")

            stop_script = target_root / ".antios" / "runtime" / "stop_gate.py"
            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            stop_payload = json.dumps({"workspacePaths": [str(target_root)]})
            proc = subprocess.run(
                [sys.executable, str(stop_script)],
                input=stop_payload,
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "continue")
            self.assertIn("conflict marker", data.get("reason", "").lower())

    def test_inspect_instance_wayfinder_cli(self):
        """Verifies that .antios/runtime/inspect_instance.py provides accurate wayfinding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            self._install_fixture(target_root, archetype="PYTHON")

            inspect_script = target_root / ".antios" / "runtime" / "inspect_instance.py"
            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONPATH"] = ""

            # 1. Summary mode
            proc = subprocess.run(
                [sys.executable, str(inspect_script), "--summary"],
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("project_name"), target_root.name)
            self.assertIn("protected_zones", data)

            # 2. Query mode
            proc = subprocess.run(
                [sys.executable, str(inspect_script), "--query", "test"],
                cwd=str(target_root),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Wayfinding Query", proc.stdout)

    def test_lifecycle_idempotency_and_clean_removal(self):
        """Verifies that reinstallation is idempotent and remove() cleans up all runtime assets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir)
            mgr = self._install_fixture(target_root, archetype="PYTHON")

            # Re-install is idempotent
            res_reinstall = mgr.install()
            self.assertIn(res_reinstall.status, ("SUCCESS", "IDEMPOTENT"))
            self.assertEqual(len(res_reinstall.issues), 0)

            # Removal cleans up .antios/runtime/
            res_rm = mgr.remove()
            self.assertEqual(res_rm.status, "SUCCESS")
            self.assertFalse((target_root / ".antios" / "runtime").exists())
            self.assertFalse((target_root / ".antios").exists())

    def test_multi_archetype_runtime_closure(self):
        """Validates that Node and Rust archetypes also achieve 100% runtime closure."""
        for arch in ["NODE", "RUST"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                target_root = Path(tmpdir)
                self._install_fixture(target_root, archetype=arch)
                result = verify_runtime_closure(target_root, execute_guards=False)
                self.assertTrue(
                    result.is_closed,
                    f"Archetype {arch} failed runtime closure: {result.violations}"
                )


if __name__ == "__main__":
    unittest.main()

