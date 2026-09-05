"""Tests for Phase 92: Agent-Native Mission Benchmark.

Verifies:
1. All 10 controlled proving-ground scenarios (A through J) are registered.
2. Explicitly labeled proxy metrics compute deterministic composite cost.
3. Comparative evaluation between BASELINE and ANTIOS workflows.
4. Catching false completions in Scenario H (Worker success claim without evidence).
5. Catching stale context in Scenario E.
6. Wayfinding bounding in Scenario I (Exploration trap).
7. Context output bounding in Scenario J.
8. Strictly bounded BenchmarkReportCard (<= 25 lines).
9. Cautious outcome language (OBSERVED_IMPROVEMENT, MEASURED_DIFFERENCE, INSUFFICIENT_DATA).
10. Benchmark safety preserving constitutional workforce limits.
"""

import unittest

from framework.core.mission_benchmark import (
    BenchmarkProxyMetric,
    BenchmarkReportCard,
    BenchmarkTrace,
    ComparisonOutcome,
    MissionBenchmarkEngine,
    ProvingGroundScenarioRegistry,
    ScenarioId,
)


class TestMissionBenchmark(unittest.TestCase):
    """Test suite for Phase 92 Agent-Native Mission Benchmark."""

    def test_ten_proving_ground_scenarios_registered(self):
        """Rule: All 10 scenarios (A through J) are registered in ProvingGroundScenarioRegistry."""
        scenarios = ProvingGroundScenarioRegistry.get_all_scenarios()
        self.assertEqual(len(scenarios), 10)
        expected_ids = {
            ScenarioId.SCENARIO_A,
            ScenarioId.SCENARIO_B,
            ScenarioId.SCENARIO_C,
            ScenarioId.SCENARIO_D,
            ScenarioId.SCENARIO_E,
            ScenarioId.SCENARIO_F,
            ScenarioId.SCENARIO_G,
            ScenarioId.SCENARIO_H,
            ScenarioId.SCENARIO_I,
            ScenarioId.SCENARIO_J,
        }
        self.assertEqual(set(scenarios.keys()), expected_ids)

    def test_proxy_metrics_computation(self):
        """Rule: BenchmarkProxyMetric computes deterministic composite cost proxy."""
        metric = BenchmarkProxyMetric(
            time_to_correct_location_proxy=2,
            unnecessary_files_inspected=1,
            context_consumed_tokens_proxy=5000,
            tool_calls_count=6,
            workforce_launches=1,
        )
        cost = metric.compute_cost_proxy()
        # 5000 * 0.001 (5.0) + 6 * 0.5 (3.0) + 1 * 5.0 (5.0) + 1 * 2.0 (2.0) = 15.0
        self.assertEqual(cost, 15.0)

    def test_simulation_scenario_a_solo_optimization(self):
        """Rule: Scenario A (Simple single-file) demonstrates observed improvement under AntiOS."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_A)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)
        self.assertLess(report.antios_cost, report.baseline_cost)
        self.assertIn("lower", report.context_reduction_proxy)

    def test_simulation_scenario_e_stale_context_refresh(self):
        """Rule: Scenario E (Stale context) shows AntiOS succeeds via refresh while Baseline fails."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_E)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        self.assertEqual(trace_base.final_verdict, "FAIL")
        self.assertEqual(trace_anti.final_verdict, "PASS")
        self.assertEqual(trace_anti.metrics.recovery_events, 1)

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)

    def test_simulation_scenario_h_worker_false_claim_rejection(self):
        """Rule: Scenario H shows Baseline accepts false completion whereas AntiOS rejects it."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_H)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        self.assertEqual(trace_base.final_verdict, "PASS")  # Erroneous self-certified pass in baseline
        self.assertEqual(trace_anti.final_verdict, "FAIL")  # Correctly failed closed in AntiOS
        self.assertFalse(trace_anti.metrics.final_correctness)

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)

    def test_simulation_scenario_i_wayfinding_exploration_trap(self):
        """Rule: Scenario I (Exploration trap) demonstrates AntiOS wayfinding bounds navigation."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_I)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        self.assertGreater(trace_base.metrics.unnecessary_files_inspected, 20)
        self.assertEqual(trace_anti.metrics.unnecessary_files_inspected, 0)
        self.assertEqual(trace_anti.metrics.time_to_correct_location_proxy, 1)

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)

    def test_simulation_scenario_j_context_pressure_bounding(self):
        """Rule: Scenario J (Oversized output) bounds tokens in AntiOS vs raw in Baseline."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_J)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        self.assertGreater(trace_base.metrics.context_consumed_tokens_proxy, 20000)
        self.assertLess(trace_anti.metrics.context_consumed_tokens_proxy, 5000)

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        self.assertEqual(report.outcome, ComparisonOutcome.OBSERVED_IMPROVEMENT)

    def test_benchmark_report_card_bounded_lines(self):
        """Rule: BenchmarkReportCard strictly adheres to <= 25 lines."""
        scenario = ProvingGroundScenarioRegistry.get_scenario(ScenarioId.SCENARIO_A)
        trace_base = MissionBenchmarkEngine.simulate_scenario(scenario, "BASELINE")
        trace_anti = MissionBenchmarkEngine.simulate_scenario(scenario, "ANTIOS")

        report = MissionBenchmarkEngine.compare_traces(trace_base, trace_anti)
        card_text = report.format_card(max_lines=25)
        lines = card_text.splitlines()

        self.assertLessEqual(len(lines), 25)
        self.assertIn("=== ANTIOS AGENT-NATIVE BENCHMARK ===", card_text)
        self.assertIn("Comparative Outcome:", card_text)

    def test_cautious_outcome_language(self):
        """Rule: Benchmark outcomes strictly adhere to cautious epistemic taxonomy."""
        outcomes = {o.value for o in ComparisonOutcome}
        self.assertEqual(
            outcomes,
            {"OBSERVED_IMPROVEMENT", "MEASURED_DIFFERENCE", "INSUFFICIENT_DATA"},
        )

    def test_identical_metrics_yield_insufficient_data(self):
        """Rule: Trace with identical cost and verdict yields INSUFFICIENT_DATA."""
        metric = BenchmarkProxyMetric(
            context_consumed_tokens_proxy=3000,
            tool_calls_count=2,
            final_correctness=True,
            evidence_completeness_ratio=1.0,
        )
        t1 = BenchmarkTrace(workflow_type="BASELINE", scenario_id="SCENARIO_A", metrics=metric, final_verdict="PASS")
        t2 = BenchmarkTrace(workflow_type="ANTIOS", scenario_id="SCENARIO_A", metrics=metric, final_verdict="PASS")

        report = MissionBenchmarkEngine.compare_traces(t1, t2)
        self.assertEqual(report.outcome, ComparisonOutcome.INSUFFICIENT_DATA)


if __name__ == "__main__":
    unittest.main()
