"""Unit & Integration Tests for AntiOS 2.0 Real Proving Ground (Phase 96)."""

import os
import sys
import tempfile
import unittest

from framework.core.proving_ground import (
    EngineeringScenario,
    ExecutionMode,
    MissionTrace,
    ProvingGroundResult,
    RealProvingGround,
    ScenarioCatalog,
    FORBIDDEN_PROVING_GROUND_TARGETS,
)


class TestProvingGroundHarness(unittest.TestCase):
    """Tests for Phase 96 Real Antigravity Proving Ground."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_pg_suite_")
        self.harness = RealProvingGround(sandbox_parent_dir=self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_canonical_catalog_contains_at_least_8_scenarios(self):
        catalog = ScenarioCatalog.get_canonical_scenarios()
        self.assertGreaterEqual(len(catalog), 8)
        expected_keys = [
            "SCENARIO_A",
            "SCENARIO_B",
            "SCENARIO_C",
            "SCENARIO_D",
            "SCENARIO_E",
            "SCENARIO_F",
            "SCENARIO_G",
            "SCENARIO_H",
        ]
        for key in expected_keys:
            self.assertIn(key, catalog)
            scenario = catalog[key]
            self.assertTrue(len(scenario.title) > 0)
            self.assertTrue(len(scenario.task_intent) > 0)
            self.assertTrue(len(scenario.acceptance_criteria) > 0)
            self.assertTrue(len(scenario.target_files) > 0)
            self.assertTrue(len(scenario.known_correct_solution) > 0)
            self.assertTrue(len(scenario.test_files) > 0)
            self.assertTrue(len(scenario.test_command) > 0)
            self.assertEqual(scenario.expected_verdict, "PASS")

    def test_mission_trace_bounds_and_summary_card(self):
        trace = MissionTrace(
            trace_id="tr-12345",
            scenario_id="SCENARIO_A",
            execution_mode=ExecutionMode.NATIVE_EXECUTION.value,
        )
        # Add 50 stage transitions (should be capped at 20)
        for i in range(50):
            trace.record_stage(f"STAGE_{i}")
        self.assertLessEqual(len(trace.stage_transitions), 20)

        # Add 50 tool calls (should be capped at 30)
        for i in range(50):
            trace.record_tool_call(f"tool_{i}", f"args_{i}", True)
        self.assertLessEqual(len(trace.tool_calls), 30)

        # Add 50 files inspected (should be capped at 30)
        for i in range(50):
            trace.record_file_inspected(f"path/to/file_{i}.py")
        self.assertLessEqual(len(trace.files_inspected), 30)

        # Summary card must be strictly <= 25 lines
        card = trace.generate_summary_card()
        lines = card.strip().split("\n")
        self.assertLessEqual(len(lines), 25)
        self.assertIn("=== Mission Trace: tr-12345 ===", card)
        self.assertIn("Mode: NATIVE_EXECUTION", card)

        # Serialization round-trip
        data = trace.to_dict()
        reconstructed = MissionTrace.from_dict(data)
        self.assertEqual(reconstructed.trace_id, trace.trace_id)
        self.assertEqual(reconstructed.trace_hash, trace.trace_hash)

    def test_fixture_safety_blocks_forbidden_paths(self):
        for forbidden in FORBIDDEN_PROVING_GROUND_TARGETS:
            bad_path = os.path.join(tempfile.gettempdir(), f"test_{forbidden}_repo")
            with self.assertRaises(PermissionError):
                self.harness._validate_fixture_safety(bad_path)

    def test_native_execution_scenario_a_passes_physically(self):
        # Physical execution of Scenario A in isolated sandbox
        result = self.harness.execute_scenario(
            "SCENARIO_A",
            execution_mode=ExecutionMode.NATIVE_EXECUTION,
            apply_fix=True,
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.execution_mode, ExecutionMode.NATIVE_EXECUTION)
        self.assertEqual(result.trace.final_verdict, "PASS")
        self.assertEqual(result.cleanup_status, "CLEANED")
        self.assertGreater(len(result.repository_fingerprint), 0)

    def test_native_execution_scenario_a_fails_closed_without_fix(self):
        result = self.harness.execute_scenario(
            "SCENARIO_A",
            execution_mode=ExecutionMode.NATIVE_EXECUTION,
            apply_fix=False,
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.trace.final_verdict, "FAIL")

    def test_simulated_trace_scenario_b(self):
        result = self.harness.execute_scenario(
            "SCENARIO_B",
            execution_mode=ExecutionMode.SIMULATED_TRACE,
            apply_fix=True,
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.execution_mode, ExecutionMode.SIMULATED_TRACE)
        self.assertEqual(result.trace.final_verdict, "PASS")

    def test_scenarios_c_through_h_execute(self):
        # Execute scenarios C through H in SIMULATED_TRACE mode to verify all catalog entries
        for sc_id in ["SCENARIO_C", "SCENARIO_D", "SCENARIO_E", "SCENARIO_F", "SCENARIO_G", "SCENARIO_H"]:
            result = self.harness.execute_scenario(
                sc_id,
                execution_mode=ExecutionMode.SIMULATED_TRACE,
                apply_fix=True,
            )
            self.assertTrue(result.passed, f"{sc_id} failed execution")
            self.assertEqual(result.trace.final_verdict, "PASS")


if __name__ == "__main__":
    unittest.main()
