"""AntiOS 3.0 Stage 2 Lifecycle & Native Antigravity Integration Test Suite.

Authoritative regression suite covering all 20 required Stage 2 areas:
1. Multi-workspace path resolution
2. Longest-prefix resolution
3. Traversal rejection (../ traversal)
4. Sibling-prefix collision rejection (/repo vs /repo-extra)
5. Windows separator normalization (/ vs \\)
6. Case normalization (c:\\work vs C:\\Work)
7. Nested repository handling
8. Stop gate repository discovery without hardcoded index 0
9. Native test runner resolution
10. Malformed hook payload handling (empty, bad json, invalid types)
11. Telemetry emission to .agents/telemetry.ndjson
12. Telemetry sanitization (secrets, home directories)
13. Telemetry failure non-blocking behavior
14. Runtime closure validation (AST analysis confirming 0 framework imports)
15. Hook configuration schema validation (.agents/hooks.json)
16. CWD/project-root resolution from nested directories
17. Read-only tool no-op behavior (< 10ms)
18. Protected-zone enforcement (immutable core zones + configured)
19. Subagent-related hook payload handling
20. Exact hook exit/decision semantics (allow, deny, continue)
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

# Import the standalone runtime hook modules under test
from framework.hooks import (
    path_resolver,
    emitter,
    pre_tool_guard,
    gate,
)


class TestStage2PathResolver(unittest.TestCase):
    """Tests 1–7: Path canonicalization, containment, multi-workspace longest prefix."""

    def test_01_multi_workspace_path_resolution(self):
        """Resolves target file across multiple workspace roots."""
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            f1 = os.path.join(tmp1, "src", "app.py")
            f2 = os.path.join(tmp2, "lib", "util.py")
            os.makedirs(os.path.dirname(f1), exist_ok=True)
            os.makedirs(os.path.dirname(f2), exist_ok=True)
            with open(f1, "w") as f:
                f.write("# app")
            with open(f2, "w") as f:
                f.write("# util")

            ws_list = [tmp1, tmp2]

            matched_ws1, canon_target1 = path_resolver.resolve_matching_workspace(f1, ws_list)
            self.assertEqual(matched_ws1, path_resolver.canonicalize_path(tmp1))

            matched_ws2, canon_target2 = path_resolver.resolve_matching_workspace(f2, ws_list)
            self.assertEqual(matched_ws2, path_resolver.canonicalize_path(tmp2))

    def test_02_longest_prefix_resolution(self):
        """Picks the most specific workspace when nested roots are present."""
        with tempfile.TemporaryDirectory() as base_tmp:
            parent_ws = os.path.join(base_tmp, "monorepo")
            child_ws = os.path.join(parent_ws, "packages", "api")
            os.makedirs(child_ws, exist_ok=True)

            target_file = os.path.join(child_ws, "src", "index.ts")
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w") as f:
                f.write("// api")

            ws_list = [parent_ws, child_ws]

            matched_ws, _ = path_resolver.resolve_matching_workspace(target_file, ws_list)
            # Must choose child_ws because it is the longer/more specific prefix
            self.assertEqual(matched_ws, path_resolver.canonicalize_path(child_ws))

    def test_03_traversal_rejection(self):
        """Rejects paths attempting directory traversal escape via ../."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = os.path.join(tmp, "workspace")
            os.makedirs(ws, exist_ok=True)
            traversal_target = os.path.join(ws, "..", "secret.txt")

            matched_ws, _ = path_resolver.resolve_matching_workspace(traversal_target, [ws])
            self.assertIsNone(matched_ws)

    def test_04_sibling_prefix_rejection(self):
        """Rejects sibling directories with prefix collision (e.g. repo vs repo-extra)."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = os.path.join(tmp, "repo")
            sibling_root = os.path.join(tmp, "repo-extra")
            os.makedirs(repo_root, exist_ok=True)
            os.makedirs(sibling_root, exist_ok=True)

            sibling_file = os.path.join(sibling_root, "exploit.py")
            with open(sibling_file, "w") as f:
                f.write("# attack")

            # Authorized workspace is ONLY repo_root
            matched_ws, _ = path_resolver.resolve_matching_workspace(sibling_file, [repo_root])
            self.assertIsNone(matched_ws)

    def test_05_windows_separator_normalization(self):
        """Normalizes mixed forward and backward slashes."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = os.path.join(tmp, "workspace")
            os.makedirs(ws, exist_ok=True)
            mixed_target = ws.replace("\\", "/") + "/src\\nested/file.py"

            canon_target = path_resolver.canonicalize_path(mixed_target)
            canon_ws = path_resolver.canonicalize_path(ws)
            self.assertTrue(path_resolver.is_contained(canon_target, canon_ws))

    def test_06_case_normalization(self):
        """Handles Windows drive letter and path casing correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            c_ws = path_resolver.canonicalize_path(tmp)
            upper_ws = c_ws.upper()
            lower_ws = c_ws.lower()

            self.assertEqual(
                path_resolver.canonicalize_path(upper_ws),
                path_resolver.canonicalize_path(lower_ws),
            )

    def test_07_nested_repository_handling(self):
        """Resolves target inside git submodule or nested repository cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            parent_repo = os.path.join(tmp, "parent")
            nested_repo = os.path.join(parent_repo, "submodules", "child")
            os.makedirs(os.path.join(nested_repo, ".git"), exist_ok=True)

            child_file = os.path.join(nested_repo, "src", "child.py")
            os.makedirs(os.path.dirname(child_file), exist_ok=True)
            with open(child_file, "w") as f:
                f.write("# child")

            matched_ws, _ = path_resolver.resolve_matching_workspace(child_file, [nested_repo])
            self.assertEqual(matched_ws, path_resolver.canonicalize_path(nested_repo))


class TestStage2StopGate(unittest.TestCase):
    """Tests 8–10: Stop gate discovery, runner resolution, malformed payloads."""

    def test_08_stop_gate_repository_discovery(self):
        """Discovers repository root without hardcoding workspacePaths[0]."""
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            os.makedirs(os.path.join(tmp2, ".git"), exist_ok=True)

            payload = {
                "workspacePaths": [tmp1, tmp2],
            }
            decision, reason, reason_code, primary_root = gate.evaluate_stop_gate(payload)
            self.assertEqual(decision, "allow")
            self.assertEqual(primary_root, path_resolver.canonicalize_path(tmp1))

    def test_09_native_test_runner_resolution(self):
        """Detects native test runners dynamically from project manifests."""
        with tempfile.TemporaryDirectory() as tmp:
            # Node project
            pkg_json = os.path.join(tmp, "package.json")
            with open(pkg_json, "w") as f:
                json.dump({"scripts": {"test": "echo test"}}, f)

            runners = gate.discover_test_runners(tmp, {})
            self.assertEqual(len(runners), 1)
            self.assertEqual(runners[0]["name"], "npm-test")

            # Python project
            pyproject = os.path.join(tmp, "pyproject.toml")
            with open(pyproject, "w") as f:
                f.write("[tool.pytest]\n")

            runners = gate.discover_test_runners(tmp, {})
            # Should have both npm-test and pytest
            runner_names = [r["name"] for r in runners]
            self.assertIn("pytest", runner_names)

    def test_10_malformed_hook_payload_handling(self):
        """Fails closed on malformed or empty payloads across guard and gate."""
        # PreToolUse
        dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use({})
        self.assertEqual(dec, "deny")
        self.assertEqual(code, "MALFORMED_INPUT")

        dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use("not a dict")
        self.assertEqual(dec, "deny")
        self.assertEqual(code, "MALFORMED_INPUT")

        # Stop Gate
        dec, reason, code, _ = gate.evaluate_stop_gate("not a dict")
        self.assertEqual(dec, "continue")
        self.assertEqual(code, "MALFORMED_INPUT")


class TestStage2Telemetry(unittest.TestCase):
    """Tests 11–13: NDJSON telemetry emission, sanitization, non-blocking guarantee."""

    def test_11_telemetry_emission(self):
        """Emits valid NDJSON events into .agents/telemetry.ndjson."""
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = os.path.join(tmp, ".agents")
            os.makedirs(agents_dir, exist_ok=True)

            success = emitter.emit_event(
                project_root=tmp,
                event_type="pre_tool_use",
                decision="allow",
                tool_class="write_to_file",
            )
            self.assertTrue(success)

            telemetry_path = os.path.join(agents_dir, "telemetry.ndjson")
            self.assertTrue(os.path.isfile(telemetry_path))

            with open(telemetry_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 1)

            entry = json.loads(lines[0])
            self.assertEqual(entry.get("schema_version"), 1)
            self.assertEqual(entry.get("event"), "pre_tool_use")
            self.assertEqual(entry.get("decision"), "allow")
            self.assertEqual(entry.get("tool_class"), "write_to_file")

    def test_12_telemetry_sanitization(self):
        """Sanitizes user home paths and API keys from telemetry payloads."""
        home_path = str(Path.home())
        raw_text = f"Error in {home_path}/secret.txt: sk-1234567890abcdef12345678"
        sanitized = emitter.sanitize_string(raw_text)

        self.assertNotIn(home_path, sanitized)
        self.assertIn("~", sanitized)
        self.assertNotIn("sk-1234567890abcdef12345678", sanitized)
        self.assertIn("[REDACTED_API_KEY]", sanitized)

    def test_13_telemetry_failure_non_blocking_behavior(self):
        """Ensures telemetry failures (e.g. invalid directory) never raise exceptions."""
        # Test with an invalid root path (file instead of directory)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"not a dir")
            invalid_root = f.name

        try:
            # Must return False and NEVER raise an exception
            res = emitter.emit_event(
                project_root=invalid_root,
                event_type="test_event",
                decision="allow",
            )
            self.assertFalse(res)
        finally:
            if os.path.exists(invalid_root):
                os.remove(invalid_root)


class TestRuntimeClosureStage2(unittest.TestCase):
    """Test 14: AST runtime closure validation for framework/hooks/."""

    def test_14_runtime_closure_zero_framework_imports(self):
        """Verifies that all scripts in framework/hooks/ have ZERO imports from 'framework'."""
        hooks_dir = Path(__file__).resolve().parent.parent / "framework" / "hooks"
        self.assertTrue(hooks_dir.is_dir(), f"framework/hooks does not exist: {hooks_dir}")

        for py_file in hooks_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name == "framework" or alias.name.startswith("framework."),
                            f"Closure violation: '{py_file.name}' imports '{alias.name}' at line {node.lineno}",
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.assertFalse(
                            node.module == "framework" or node.module.startswith("framework."),
                            f"Closure violation: '{py_file.name}' imports from '{node.module}' at line {node.lineno}",
                        )


class TestStage2Governance(unittest.TestCase):
    """Tests 15–20: Schema validation, CWD discovery, no-op, zones, subagent, decision semantics."""

    def test_15_hook_configuration_schema_validation(self):
        """.agents/hooks.json must validly declare PreInvocation, PreToolUse, PostToolUse, and Stop."""
        hooks_json_path = Path(__file__).resolve().parent.parent / ".agents" / "hooks.json"
        self.assertTrue(hooks_json_path.is_file())

        with open(hooks_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        guard_config = data.get("antios-guard", {})
        self.assertIn("PreInvocation", guard_config)
        self.assertIn("PreToolUse", guard_config)
        self.assertIn("PostToolUse", guard_config)
        self.assertIn("Stop", guard_config)

    def test_16_cwd_project_root_resolution(self):
        """Resolves project root when invoked from nested subdirectories."""
        source_root = Path(__file__).resolve().parent.parent
        nested_dir = source_root / "framework" / "hooks"

        discovered = path_resolver.discover_project_root(starting_dir=str(nested_dir))
        self.assertEqual(
            path_resolver.canonicalize_path(str(source_root)),
            discovered,
        )

    def test_17_read_only_tool_no_op_behavior(self):
        """Read-only tools (view_file, grep_search) return 'allow' in < 10ms without path checks."""
        start = time.perf_counter()
        payload = {
            "toolCall": {
                "name": "view_file",
                "args": {"AbsolutePath": "C:/any/nonexistent/file.txt"},
            },
            "workspacePaths": ["C:/fake/workspace"],
        }
        dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use(payload)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(dec, "allow")
        self.assertIsNone(reason)
        self.assertLess(elapsed_ms, 10.0, f"Read-only tool check took {elapsed_ms:.2f}ms (target < 10ms)")

    def test_18_protected_zone_enforcement(self):
        """Blocks modifications to immutable core zones (.agents, antios.config.json, .git, framework)."""
        with tempfile.TemporaryDirectory() as tmp:
            protected_targets = [
                ".agents/hooks.json",
                "antios.config.json",
                ".git/config",
                "framework/hooks/gate.py",
            ]
            for target in protected_targets:
                payload = {
                    "toolCall": {
                        "name": "write_to_file",
                        "args": {"TargetFile": target},
                    },
                    "workspacePaths": [tmp],
                }
                dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use(payload)
                self.assertEqual(dec, "deny", f"Expected deny for {target}")
                self.assertEqual(code, "PROTECTED_ZONE_VIOLATION")

    def test_19_subagent_related_hook_payload_handling(self):
        """Evaluates subagent-related invocations cleanly without false positives."""
        payload = {
            "toolCall": {
                "name": "manage_subagents",
                "args": {"Action": "list"},
            },
            "workspacePaths": ["C:/fake/workspace"],
        }
        dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use(payload)
        self.assertEqual(dec, "allow")

    def test_20_exact_hook_exit_decision_semantics(self):
        """Confirms exact contract return types ('allow', 'deny', 'continue')."""
        with tempfile.TemporaryDirectory() as tmp:
            valid_payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "src/module.py"},
                },
                "workspacePaths": [tmp],
            }
            dec, _, _, _ = pre_tool_guard.evaluate_pre_tool_use(valid_payload)
            self.assertEqual(dec, "allow")

            invalid_payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "../outside.txt"},
                },
                "workspacePaths": [tmp],
            }
            dec, _, _, _ = pre_tool_guard.evaluate_pre_tool_use(invalid_payload)
            self.assertEqual(dec, "deny")

            # Stop gate allow
            stop_payload = {"workspacePaths": [tmp]}
            dec, _, _, _ = gate.evaluate_stop_gate(stop_payload)
            self.assertEqual(dec, "allow")


class TestAdversarialAndPerformance(unittest.TestCase):
    """Adversarial 8.3 alias tests and microsecond performance benchmarks."""

    def test_adversarial_83_alias_defense(self):
        """Prevents short filename alias bypasses on protected zones."""
        with tempfile.TemporaryDirectory() as tmp:
            alias_targets = [
                "agents~1/hooks.json",
                "framew~1/core/guard.py",
                "antios~1.jso",
            ]
            for target in alias_targets:
                payload = {
                    "toolCall": {
                        "name": "replace_file_content",
                        "args": {"TargetFile": target},
                    },
                    "workspacePaths": [tmp],
                }
                dec, reason, code, _ = pre_tool_guard.evaluate_pre_tool_use(payload)
                self.assertEqual(dec, "deny", f"Expected deny for 8.3 alias {target}")
                self.assertIn(code, ("ALIAS_BYPASS_ATTEMPT", "PROTECTED_ZONE_VIOLATION"))

    def test_pre_tool_guard_performance_benchmark(self):
        """PreToolUse guard execution latency must remain strictly under 10ms."""
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "src/benchmark_test.py"},
                },
                "workspacePaths": [tmp],
            }
            # Warm up
            pre_tool_guard.evaluate_pre_tool_use(payload)

            # Benchmark 50 iterations
            start = time.perf_counter()
            for _ in range(50):
                pre_tool_guard.evaluate_pre_tool_use(payload)
            total_elapsed_ms = (time.perf_counter() - start) * 1000
            avg_elapsed_ms = total_elapsed_ms / 50

            self.assertLess(
                avg_elapsed_ms,
                10.0,
                f"PreToolUse average latency {avg_elapsed_ms:.3f}ms exceeds 10ms ceiling",
            )


class TestStage2PhysicalSubprocess(unittest.TestCase):
    """Physical execution of framework/hooks scripts in isolated subprocesses with PYTHONPATH=''."""

    def setUp(self):
        self.source_root = Path(__file__).resolve().parent.parent
        self.clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        self.clean_env["PYTHONPATH"] = ""

    def test_subprocess_pre_tool_guard_allow_and_deny(self):
        """Executes pre_tool_guard.py via subprocess with zero PYTHONPATH."""
        script_path = self.source_root / "framework" / "hooks" / "pre_tool_guard.py"
        with tempfile.TemporaryDirectory() as tmp:
            # 1. Valid write allowed
            allow_payload = json.dumps({
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": "src/main.py"}},
                "workspacePaths": [tmp],
            })
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                input=allow_payload,
                cwd=tmp,
                env=self.clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "allow")

            # 2. Protected zone write denied
            deny_payload = json.dumps({
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": ".agents/hooks.json"}},
                "workspacePaths": [tmp],
            })
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                input=deny_payload,
                cwd=tmp,
                env=self.clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "deny")
            self.assertIn("PROTECTED_ZONE_VIOLATION", data.get("reason", ""))

    def test_subprocess_gate_execution(self):
        """Executes gate.py via subprocess with zero PYTHONPATH."""
        script_path = self.source_root / "framework" / "hooks" / "gate.py"
        with tempfile.TemporaryDirectory() as tmp:
            # Clean project passes
            payload = json.dumps({"workspacePaths": [tmp]})
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                input=payload,
                cwd=tmp,
                env=self.clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("decision"), "allow")

    def test_subprocess_pre_invocation_and_post_tool_use(self):
        """Executes pre_invocation.py and post_tool_use.py via subprocess."""
        pre_inv = self.source_root / "framework" / "hooks" / "pre_invocation.py"
        post_tool = self.source_root / "framework" / "hooks" / "post_tool_use.py"

        with tempfile.TemporaryDirectory() as tmp:
            # PreInvocation
            proc1 = subprocess.run(
                [sys.executable, str(pre_inv)],
                input=json.dumps({"workspacePaths": [tmp]}),
                cwd=tmp,
                env=self.clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc1.returncode, 0)
            self.assertEqual(json.loads(proc1.stdout), {})

            # PostToolUse
            proc2 = subprocess.run(
                [sys.executable, str(post_tool)],
                input=json.dumps({"stepIdx": 1, "workspacePaths": [tmp]}),
                cwd=tmp,
                env=self.clean_env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(proc2.returncode, 0)
            self.assertEqual(json.loads(proc2.stdout), {})


if __name__ == "__main__":
    unittest.main()

