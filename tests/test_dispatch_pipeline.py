"""Unit tests for the AntiOS 2.0 Task Dispatch Pipeline."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from framework.core.dispatch import MissionPlan, TaskClassificationResult, TaskDispatchPipeline
from framework.core.lifecycle import RiskTier, TaskClass
from framework.core.orchestration import CoordinationLevel, WorkforceMode, WriteSafetyPolicy


class TestDispatchPipeline(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.pipeline = TaskDispatchPipeline(workspace_root=str(self.repo_root))

    def test_classify_task_classes_and_risks(self):
        # Bug classification
        res_bug = self.pipeline.classify_task("Fix crash in adapter test failure")
        self.assertEqual(res_bug.task_class, TaskClass.BUG)

        # Refactor classification (High risk)
        res_refactor = self.pipeline.classify_task("Refactor state transitions in orchestration")
        self.assertEqual(res_refactor.task_class, TaskClass.REFACTOR)
        self.assertEqual(res_refactor.risk_tier, RiskTier.HIGH)

        # Documentation classification (Low risk)
        res_doc = self.pipeline.classify_task("Update README and architecture documentation")
        self.assertEqual(res_doc.task_class, TaskClass.DOCUMENTATION)
        self.assertEqual(res_doc.risk_tier, RiskTier.LOW)

        # Investigation classification
        res_inv = self.pipeline.classify_task("Investigate memory consumption in worker pool")
        self.assertEqual(res_inv.task_class, TaskClass.INVESTIGATION)

        # Security/Auth feature (High risk)
        res_sec = self.pipeline.classify_task("Implement oauth token auth authentication endpoint")
        self.assertEqual(res_sec.task_class, TaskClass.FEATURE)
        self.assertEqual(res_sec.risk_tier, RiskTier.HIGH)

        # Explicit delegation detection
        res_del = self.pipeline.classify_task("Run parallel investigation with multiple agents")
        self.assertTrue(res_del.explicit_delegation)

    def test_dispatch_solo_documentation_task(self):
        plan = self.pipeline.dispatch("Update documentation for main antios skill")
        self.assertEqual(plan.task_class, TaskClass.DOCUMENTATION.value)
        self.assertEqual(plan.risk_tier, RiskTier.LOW.value)
        self.assertEqual(plan.workforce_mode, WorkforceMode.SOLO)
        self.assertEqual(plan.coordination_level, CoordinationLevel.L0)
        self.assertEqual(len(plan.initial_waves), 3)  # PLANNING, IMPLEMENTATION, VERIFICATION

        # Check format card token bounding
        card = plan.format_card(max_lines=25)
        lines = card.splitlines()
        self.assertLessEqual(len(lines), 25)
        self.assertIn("ANTIOS MISSION DISPATCH CARD", card)
        self.assertIn("Workforce:    SOLO", card)

    def test_dispatch_multi_stream_parallel_task(self):
        plan = self.pipeline.dispatch(
            task_query="Refactor database schema and migrate storage adapters",
            independent_streams=3,
            workstream_count=3,
        )
        self.assertEqual(plan.workforce_mode, WorkforceMode.PARALLEL)
        self.assertEqual(plan.coordination_level, CoordinationLevel.L2)
        self.assertGreaterEqual(plan.execution_gate.recommended_workers, 3)
        self.assertEqual(len(plan.initial_waves), 5)  # RECONNAISSANCE -> PLANNING -> IMPLEMENTATION -> VERIFICATION -> DELIVERY

    def test_dispatch_explicit_mode_override(self):
        plan = self.pipeline.dispatch(
            task_query="Inspect lint errors",
            explicit_mode="SMALL",
        )
        self.assertEqual(plan.workforce_mode, WorkforceMode.SMALL)

    def test_dispatch_task_cli_execution(self):
        cli_script = self.repo_root / "framework" / "scripts" / "tools" / "dispatch_task.py"
        self.assertTrue(cli_script.is_file(), "dispatch_task.py CLI tool must exist")

        cmd = [sys.executable, str(cli_script), "Fix broken parser exception in parser.py", "--json"]
        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0, f"CLI dispatch failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertIn("mission_id", data)
        self.assertEqual(data["task_class"], "BUG")
        self.assertIn("workforce_mode", data)
        self.assertIn("configured_test_command", data)


if __name__ == "__main__":
    unittest.main()
