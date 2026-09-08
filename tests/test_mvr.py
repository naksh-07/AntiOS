"""AntiOS 3.0 Tests: 6-Dimension MVR Verification Engine & Stop Gate Enforcement.

Constitutional Invariants:
- INV-03: Physical verification required (exit code 0).
- INV-04: Fail-closed boundary enforcement.
- INV-10: 4-Zone ownership boundary.
- INV-11: Zero third-party dependencies (unittest + stdlib).
- INV-15: Zero background daemons (synchronous execution).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from framework.hooks.gate import (
    CONFLICT_MARKERS,
    MVR_FAIL_FAST_ORDER,
    check_working_tree_conflicts,
    discover_test_runners,
    evaluate_stop_gate,
    run_command_safe,
    sanitize_command,
)


class TestMVRStopGate(unittest.TestCase):
    """Verifies 6-dimension MVR verification, anti-watch sanitization, and Stop Gate ratchets."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_test_mvr_")
        # Initialize bare test workspace with antios.config.json
        self.config_path = os.path.join(self.test_dir, "antios.config.json")
        self.config_data = {
            "version": "3.0",
            "name": "MVR-Test-Adapter",
            "verification": {
                "lint": {
                    "name": "lint",
                    "command": [sys.executable, "-c", "import sys; sys.exit(0)"],
                    "timeout_seconds": 10,
                    "required": False,
                },
                "unit_test": {
                    "name": "unit",
                    "command": [sys.executable, "-c", "import sys; sys.exit(0)"],
                    "timeout_seconds": 10,
                    "required": True,
                },
            },
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_conflict_markers_detection_standard(self):
        """Standard git conflict markers (<<<, ===, >>>) are detected and block completion."""
        dirty_file = os.path.join(self.test_dir, "conflict.py")
        with open(dirty_file, "w", encoding="utf-8") as f:
            f.write("<<<<<<< HEAD\nprint('ours')\n=======\nprint('theirs')\n>>>>>>> branch\n")

        err = check_working_tree_conflicts(self.test_dir)
        self.assertIsNotNone(err)
        self.assertIn("Unresolved conflict marker", err)

        # Stop Gate evaluation
        input_data = {"workspacePaths": [self.test_dir]}
        decision, reason, code, _ = evaluate_stop_gate(input_data)
        self.assertEqual(decision, "continue")
        self.assertEqual(code, "CONFLICT_MARKERS")

    def test_conflict_markers_detection_diff3_base(self):
        """diff3 base conflict marker (|||||||) is detected and blocks completion."""
        dirty_file = os.path.join(self.test_dir, "conflict_diff3.py")
        with open(dirty_file, "w", encoding="utf-8") as f:
            f.write("||||||| merged common ancestors\nprint('base')\n=======\nprint('ours')\n>>>>>>> branch\n")

        err = check_working_tree_conflicts(self.test_dir)
        self.assertIsNotNone(err)
        self.assertIn("Unresolved conflict marker", err)
        self.assertIn("|||||||", err)

        input_data = {"workspacePaths": [self.test_dir]}
        decision, reason, code, _ = evaluate_stop_gate(input_data)
        self.assertEqual(decision, "continue")
        self.assertEqual(code, "CONFLICT_MARKERS")

    def test_anti_watch_command_sanitizer(self):
        """Anti-watch sanitizer removes hazardous watch flags and appends non-watch arguments."""
        # Vitest
        cmd_vitest = sanitize_command(["npm", "run", "vitest"])
        self.assertIn("--run", cmd_vitest)

        # Jest with bare watch
        cmd_jest = sanitize_command(["jest", "--watch"])
        self.assertNotIn("--watch", cmd_jest)
        self.assertIn("--watch=false", cmd_jest)
        self.assertIn("--watchAll=false", cmd_jest)

        # General npm test
        cmd_npm = sanitize_command(["npm", "test"])
        self.assertIn("--watchAll=false", cmd_npm)

        # Safe command untouched
        cmd_safe = sanitize_command(["python", "tests/run_all.py"])
        self.assertEqual(cmd_safe, ["python", "tests/run_all.py"])

    def test_mvr_discover_test_runners_order(self):
        """MVR runners are resolved in strict fail-fast order."""
        full_mvr_config = {
            "verification": {
                "unit_test": {"command": ["python", "test_unit.py"], "required": True},
                "lint": {"command": ["ruff", "check"], "required": False},
                "typecheck": {"command": ["mypy"], "required": False},
            }
        }
        runners = discover_test_runners(self.test_dir, full_mvr_config)
        self.assertEqual(len(runners), 3)
        # Order must be lint -> typecheck -> unit_test
        dimensions = [r["dimension"] for r in runners]
        self.assertEqual(dimensions, ["lint", "typecheck", "unit_test"])

    def test_stop_gate_success_and_report_caching(self):
        """Successful verification returns 'allow' and caches verification report."""
        input_data = {"workspacePaths": [self.test_dir]}
        decision, reason, code, root = evaluate_stop_gate(input_data)
        self.assertEqual(decision, "allow")
        self.assertIsNone(reason)

        # Report must be cached to .agents/cache/last_verification_report.json
        report_path = os.path.join(self.test_dir, ".agents", "cache", "last_verification_report.json")
        self.assertTrue(os.path.isfile(report_path), "Verification report must be cached")
        with open(report_path, "r", encoding="utf-8") as fp:
            report = json.load(fp)
        self.assertEqual(report["verdict"], "allow")
        self.assertEqual(len(report["executed_runners"]), 2)

    def test_stop_gate_physical_test_failure_blocks_completion(self):
        """Non-zero exit in required test runner physically blocks completion."""
        failing_config = {
            "version": "3.0",
            "verification": {
                "unit_test": {
                    "name": "failing-tests",
                    "command": [sys.executable, "-c", "import sys; sys.stderr.write('CRITICAL FAILURE'); sys.exit(2)"],
                    "timeout_seconds": 10,
                    "required": True,
                }
            }
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(failing_config, f)

        input_data = {"workspacePaths": [self.test_dir]}
        decision, reason, code, root = evaluate_stop_gate(input_data)
        self.assertEqual(decision, "continue")
        self.assertEqual(code, "TEST_FAILURE")
        self.assertIn("CRITICAL FAILURE", reason)

        # Report cached as continue
        report_path = os.path.join(self.test_dir, ".agents", "cache", "last_verification_report.json")
        self.assertTrue(os.path.isfile(report_path))
        with open(report_path, "r", encoding="utf-8") as fp:
            report = json.load(fp)
        self.assertEqual(report["verdict"], "continue")

    def test_stop_gate_missing_required_runner_fails_closed(self):
        """Missing required test executable triggers fail-closed rejection."""
        missing_config = {
            "version": "3.0",
            "verification": {
                "unit_test": {
                    "name": "nonexistent-tool",
                    "command": ["this_tool_does_not_exist_xyz123"],
                    "timeout_seconds": 10,
                    "required": True,
                }
            }
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(missing_config, f)

        input_data = {"workspacePaths": [self.test_dir]}
        decision, reason, code, root = evaluate_stop_gate(input_data)
        self.assertEqual(decision, "continue")
        self.assertEqual(code, "MISSING_TEST_RUNNER")


if __name__ == "__main__":
    unittest.main()
